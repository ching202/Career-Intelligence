"""Export a reproducible synthetic example for the Week 8 analytics milestone."""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from career_intelligence.analytics import Filters, filter_jobs, grouped_summary, safe_csv, skill_demand, summary
from career_intelligence.data import load_csv


def run(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    fixture = ROOT / "tests/fixtures/analytics_cases.csv"
    jobs = load_csv(fixture).jobs
    frames = {
        "annualized_salaries.csv": jobs[["job_id", "salary_period", "salary_min", "salary_max", "annual_min_usd", "annual_max_usd", "salary_mid_usd", "salary_status"]],
        "languages.csv": skill_demand(jobs),
        "locations.csv": grouped_summary(jobs, "location"),
        "work_modes.csv": grouped_summary(jobs, "work_mode"),
        "experience_levels.csv": grouped_summary(jobs, "experience_level"),
        "seattle_remote_locations.csv": grouped_summary(
            filter_jobs(jobs, Filters(locations=("Seattle, WA",), work_modes=("Remote",))), "location"
        ),
    }
    for name, frame in frames.items():
        (output / name).write_bytes(safe_csv(frame))
    record = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution": "AI-assisted automated verification; not student practicum hours",
        "dataset": "Seven fictional job records; not labor-market evidence",
        "fixture_sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(),
        "summary": summary(jobs),
    }
    (output / "summary.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record["summary"], indent=2))
    print(f"Saved six CSV examples and summary metadata to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/week8-analytics")
    run(parser.parse_args().output.resolve())
