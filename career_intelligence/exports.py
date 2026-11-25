"""Portable snapshots of the displayed dashboard view, without server-side files."""

import json
from dataclasses import asdict
from datetime import datetime, timezone
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd

from career_intelligence.analytics import Filters, export_jobs, grouped_summary, safe_csv, skill_demand, summary


def export_view_bundle(
    jobs: pd.DataFrame,
    filters: Filters,
    *,
    dataset_sha256: str,
    validated_jobs: int,
    languages_only: bool = True,
) -> bytes:
    """Bundle an already-filtered view and the settings used to select its records."""
    settings = asdict(filters)
    for name in ("date_start", "date_end"):
        settings[name] = settings[name].isoformat() if settings[name] is not None else None
    record = {
        "schema_version": 1,
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_sha256": dataset_sha256,
        "validated_jobs": int(validated_jobs),
        "filters": settings,
        "language_scope": "Languages and SQL" if languages_only else "All skill tokens",
        "summary": summary(jobs),
        "notes": [
            "CSV files describe the displayed filtered view, not the whole input file.",
            "The source SHA-256 identifies the loaded file; that original file is not included.",
            "Salaries use comparable USD range midpoints; missing pay is not zero.",
            "The original data_source label is retained in filtered_jobs.csv.",
            "CSV text beginning with spreadsheet formula prefixes is escaped.",
        ],
    }
    files = {
        "filtered_jobs.csv": export_jobs(jobs),
        "language_demand.csv": safe_csv(skill_demand(jobs, languages_only=languages_only)),
        "location_summary.csv": safe_csv(grouped_summary(jobs, "location")),
        "view_summary.json": (json.dumps(record, indent=2, allow_nan=False) + "\n").encode("utf-8"),
    }
    output = BytesIO()
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return output.getvalue()
