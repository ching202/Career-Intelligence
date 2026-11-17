"""Validate untrusted CSV data and retain an auditable cleaning report.

No networking, currency conversion, salary imputation, or free-text skill inference.
"""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

MAX_BYTES = 10 * 1024 * 1024
MAX_ROWS = 50_000
REQUIRED_COLUMNS = (
    "job_id", "title", "company", "location", "work_mode", "experience_level",
    "salary_min", "salary_max", "salary_currency", "salary_period", "skills",
    "posted_date", "data_source",
)
PAY_FACTORS = {"annual": 1, "monthly": 12, "weekly": 52, "hourly": 2080}
LANGUAGES = frozenset({
    "Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#", "Go",
    "Rust", "Ruby", "PHP", "Swift", "Kotlin", "R", "Scala", "SQL", "Dart", "Bash",
})
SKILL_ALIASES = {name.casefold(): name for name in LANGUAGES | {
    "React", "Node.js", "Django", "Flask", "FastAPI", "Spring", ".NET", "AWS",
    "Azure", "Docker", "Kubernetes", "Git", "PostgreSQL", "Linux", "Pandas",
    "TensorFlow", "Vue", "Angular", "HTML", "CSS",
}}
SKILL_ALIASES.update({
    "py": "Python", "js": "JavaScript", "ts": "TypeScript", "golang": "Go",
    "csharp": "C#", "c sharp": "C#", "cpp": "C++", "nodejs": "Node.js",
    "node": "Node.js", "postgres": "PostgreSQL", "react.js": "React",
})


class DataValidationError(ValueError):
    """An input cannot be safely interpreted using the documented CSV schema."""


@dataclass
class Dataset:
    jobs: pd.DataFrame
    issues: pd.DataFrame
    input_rows: int
    dropped_rows: int


def parse_skills(value: str) -> tuple[str, ...]:
    """Normalize explicit skill tokens; Java never matches JavaScript."""
    normalized = {}
    for part in re.split(r"[;,|]", str(value)):
        token = part.strip()
        if token:
            canonical = SKILL_ALIASES.get(token.casefold(), token)
            normalized.setdefault(canonical.casefold(), canonical)
    return tuple(sorted(normalized.values(), key=str.casefold))


def load_csv(source: Path | bytes) -> Dataset:
    """Read UTF-8 CSV bytes or a trusted local path with size/row limits."""
    if isinstance(source, Path):
        if source.stat().st_size > MAX_BYTES:
            raise DataValidationError("CSV exceeds the 10 MiB limit.")
        raw = source.read_bytes()
    else:
        raw = source
    if len(raw) > MAX_BYTES:
        raise DataValidationError("CSV exceeds the 10 MiB limit.")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DataValidationError("Save your CSV as UTF-8, then try again.") from exc
    if "\x00" in text:
        raise DataValidationError("The CSV contains binary/null characters.")
    try:
        # Check headers before pandas can silently rename duplicate columns.
        reader = csv.reader(io.StringIO(text), strict=True)
        header = next(reader)
        header = [name.strip().lower() for name in header]
        if len(header) != len(set(header)):
            raise DataValidationError("CSV column names must be unique.")
        missing = set(REQUIRED_COLUMNS) - set(header)
        if missing:
            raise DataValidationError("Missing required columns: " + ", ".join(sorted(missing)))
        # Reject ragged records, including short rows that pandas would fill silently.
        for row_number, row in enumerate(reader, 2):
            if row_number > MAX_ROWS + 1:
                raise DataValidationError("CSV exceeds the 50,000-row limit.")
            if len(row) != len(header):
                raise DataValidationError(f"CSV record {row_number} has {len(row)} fields; expected {len(header)}.")
        frame = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
        frame.columns = header
    except (StopIteration, pd.errors.EmptyDataError) as exc:
        raise DataValidationError("The CSV is empty. Include a header and at least one job.") from exc
    except (csv.Error, pd.errors.ParserError) as exc:
        raise DataValidationError("The CSV is malformed. Check delimiters and quotation marks.") from exc
    if frame.empty:
        raise DataValidationError("The CSV has a header but no job rows.")
    return clean_jobs(frame)


def clean_jobs(frame: pd.DataFrame) -> Dataset:
    """Keep countable jobs even when salary or date fields are unusable."""
    missing = set(REQUIRED_COLUMNS) - set(frame.columns)
    if missing:
        raise DataValidationError("Missing required columns: " + ", ".join(sorted(missing)))
    jobs = frame.loc[:, REQUIRED_COLUMNS].copy().fillna("")
    for col in REQUIRED_COLUMNS:
        jobs[col] = jobs[col].astype(str).str.strip()
    jobs["source_row"] = range(2, len(jobs) + 2)
    input_rows = len(jobs)
    issues = []

    def flag(mask: pd.Series, issue: str, action: str) -> None:
        for _, row in jobs.loc[mask, ["source_row", "job_id"]].iterrows():
            issues.append({"csv_record": int(row.source_row), "job_id": row.job_id,
                           "issue": issue, "action": action})

    invalid = jobs[["job_id", "title", "location"]].eq("").any(axis=1)
    flag(invalid, "Missing job_id, title, or location", "Row dropped")
    jobs = jobs.loc[~invalid].copy()
    duplicates = jobs.duplicated("job_id", keep="first")
    flag(duplicates, "Duplicate job_id", "Row dropped; first valid identity kept")
    jobs = jobs.loc[~duplicates].copy()
    jobs["company"] = jobs.company.replace("", "Unknown")
    jobs["data_source"] = jobs.data_source.replace("", "Unspecified")

    mode_map = {"remote": "Remote", "hybrid": "Hybrid", "on-site": "On-site",
                "onsite": "On-site", "on site": "On-site", "unknown": "Unknown"}
    level_map = {v.lower(): v for v in ["Internship", "Entry", "Mid", "Senior", "Lead", "Unknown"]}
    level_map.update({"junior": "Entry", "entry-level": "Entry", "mid-level": "Mid"})
    for col, mapping in [("work_mode", mode_map), ("experience_level", level_map)]:
        mapped = jobs[col].str.lower().map(mapping)
        flag(mapped.isna(), f"Unrecognized {col}", "Set to Unknown")
        jobs[col] = mapped.fillna("Unknown")

    jobs["skill_tokens"] = jobs.skills.map(parse_skills)
    jobs["skills"] = jobs.skill_tokens.map(";".join)
    flag(jobs.skills.eq(""), "No skill tokens", "Retained in demand denominator")
    jobs["salary_currency"] = jobs.salary_currency.str.upper()
    jobs["salary_period"] = jobs.salary_period.str.lower().replace({
        "yearly": "annual", "year": "annual", "month": "monthly", "week": "weekly", "hour": "hourly",
    })
    low = pd.to_numeric(jobs.salary_min, errors="coerce")
    high = pd.to_numeric(jobs.salary_max, errors="coerce")
    factor = jobs.salary_period.map(PAY_FACTORS)
    missing_salary = jobs.salary_min.eq("") & jobs.salary_max.eq("")
    valid_numbers = low.gt(0) & high.ge(low) & np.isfinite(low) & np.isfinite(high)
    with np.errstate(over="ignore", invalid="ignore"):
        annual_low, annual_high = low * factor, high * factor
        midpoint = annual_low / 2 + annual_high / 2
    valid_numbers &= np.isfinite(annual_low) & np.isfinite(annual_high) & np.isfinite(midpoint)
    status = pd.Series("Included (USD)", index=jobs.index)
    status.loc[~valid_numbers] = "Invalid salary"
    status.loc[factor.isna()] = "Unknown pay period"
    status.loc[jobs.salary_currency.ne("USD")] = "Unsupported currency"
    status.loc[missing_salary] = "Missing salary"
    jobs["salary_status"] = status
    included = status.eq("Included (USD)")
    jobs["annual_min_usd"] = annual_low.where(included)
    jobs["annual_max_usd"] = annual_high.where(included)
    jobs["salary_mid_usd"] = midpoint.where(included)
    for value in sorted(set(status) - {"Included (USD)"}):
        flag(status.eq(value), value, "Excluded from salary statistics; job retained")

    iso_date = jobs.posted_date.str.fullmatch(r"\d{4}-\d{2}-\d{2}")
    parsed_date = pd.to_datetime(jobs.posted_date.where(iso_date), format="%Y-%m-%d", errors="coerce")
    flag(parsed_date.isna(), "Missing or invalid posted_date", "Excluded from date chart")
    jobs["posted_date"] = parsed_date
    jobs = jobs.reset_index(drop=True)
    audit = pd.DataFrame(issues, columns=["csv_record", "job_id", "issue", "action"])
    return Dataset(jobs, audit, input_rows, input_rows - len(jobs))
