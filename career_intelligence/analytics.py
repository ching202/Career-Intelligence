"""Pure analysis functions used by both the dashboard and automated tests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from career_intelligence.data import LANGUAGES, REQUIRED_COLUMNS


@dataclass(frozen=True)
class Filters:
    query: str = ""
    locations: tuple[str, ...] = ()
    work_modes: tuple[str, ...] = ()
    levels: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    match_all: bool = False
    min_salary: float = 0
    include_missing_salary: bool = True
    date_start: date | None = None
    date_end: date | None = None
    include_undated: bool = True


def filter_jobs(jobs: pd.DataFrame, options: Filters) -> pd.DataFrame:
    mask = pd.Series(True, index=jobs.index)
    query = options.query.strip()
    if query:
        # Literal search prevents regex input from changing search meaning.
        mask &= (jobs.title.str.contains(query, case=False, regex=False)
                 | jobs.company.str.contains(query, case=False, regex=False))
    for column, selected in [("location", options.locations), ("work_mode", options.work_modes),
                             ("experience_level", options.levels)]:
        if selected:
            mask &= jobs[column].isin(selected)
    if options.languages:
        wanted = set(options.languages)
        mask &= jobs.skill_tokens.map(
            lambda tokens: wanted.issubset(tokens) if options.match_all else bool(wanted.intersection(tokens))
        ).astype(bool)
    salary_mask = jobs.salary_mid_usd.ge(options.min_salary)
    if options.include_missing_salary:
        salary_mask |= jobs.salary_mid_usd.isna()
    mask &= salary_mask
    if options.date_start is not None or options.date_end is not None:
        date_mask = jobs.posted_date.notna()
        if options.date_start is not None:
            date_mask &= jobs.posted_date.ge(pd.Timestamp(options.date_start))
        if options.date_end is not None:
            date_mask &= jobs.posted_date.le(pd.Timestamp(options.date_end))
        if options.include_undated:
            date_mask |= jobs.posted_date.isna()
        mask &= date_mask
    return jobs.loc[mask].copy()


def summary(jobs: pd.DataFrame) -> dict[str, int | float | None]:
    salary = jobs.salary_mid_usd.dropna()
    count = len(jobs)
    return {
        "jobs": count,
        "median_salary": float(salary.median()) if len(salary) else None,
        "salary_count": len(salary),
        "salary_coverage": 100 * len(salary) / count if count else 0.0,
        "remote_share": 100 * jobs.work_mode.eq("Remote").sum() / count if count else 0.0,
        "locations": jobs.location.nunique(),
    }


def skill_demand(jobs: pd.DataFrame, languages_only: bool = True) -> pd.DataFrame:
    rows = jobs[["job_id", "skill_tokens"]].explode("skill_tokens").dropna()
    rows = rows.drop_duplicates(["job_id", "skill_tokens"])
    if languages_only:
        rows = rows.loc[rows.skill_tokens.isin(LANGUAGES)]
    counts = rows.groupby("skill_tokens").size().rename("jobs").reset_index().rename(columns={"skill_tokens": "skill"})
    counts["share_pct"] = counts.jobs / len(jobs) * 100 if len(jobs) else 0.0
    return counts.sort_values(["jobs", "skill"], ascending=[False, True]).reset_index(drop=True)


def grouped_summary(jobs: pd.DataFrame, group: str) -> pd.DataFrame:
    if group not in {"location", "experience_level", "work_mode"}:
        raise ValueError("Unsupported grouping column")
    result = jobs.groupby(group).agg(
        jobs=("job_id", "size"), salary_count=("salary_mid_usd", "count"),
        median_salary=("salary_mid_usd", "median"),
    ).reset_index()
    # Each group's denominator includes its jobs without comparable USD salaries.
    result["salary_coverage"] = 100 * result.salary_count / result.jobs
    return result.sort_values(["jobs", group], ascending=[False, True]).reset_index(drop=True)


def posting_activity(jobs: pd.DataFrame) -> pd.DataFrame:
    valid = jobs.loc[jobs.posted_date.notna()]
    if valid.empty:
        return pd.DataFrame(columns=["week", "jobs"])
    # W-SUN means Monday-start weeks ending Sunday.
    weeks = valid.posted_date.dt.to_period("W-SUN").dt.start_time
    counts = weeks.value_counts().sort_index()
    complete = pd.date_range(counts.index.min(), counts.index.max(), freq="W-MON")
    return counts.reindex(complete, fill_value=0).rename_axis("week").reset_index(name="jobs")


def safe_csv(frame: pd.DataFrame) -> bytes:
    """Escape spreadsheet formula prefixes without executing or losing plain CSV data."""
    export = frame.copy()
    for column in export.select_dtypes(include=["object", "string"]).columns:
        export[column] = export[column].map(
            lambda value: "'" + value if isinstance(value, str)
            and (value.startswith(("\t", "\r", "\n")) or value.lstrip().startswith(("=", "+", "-", "@")))
            else value
        )
    return export.to_csv(index=False, lineterminator="\n").encode("utf-8-sig")


def export_jobs(jobs: pd.DataFrame) -> bytes:
    columns = list(REQUIRED_COLUMNS) + ["annual_min_usd", "annual_max_usd", "salary_mid_usd", "salary_status"]
    export = jobs.loc[:, columns].copy()
    export["posted_date"] = export.posted_date.dt.strftime("%Y-%m-%d").fillna("")
    return safe_csv(export)
