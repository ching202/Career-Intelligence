from datetime import date
from io import BytesIO

import pandas as pd
import pytest

from career_intelligence.analytics import (
    Filters, export_jobs, filter_jobs, grouped_summary, posting_activity, safe_csv, skill_demand, summary,
)
from career_intelligence.data import load_csv


def test_metrics_use_only_comparable_salaries(jobs):
    result = summary(jobs)
    assert result["jobs"] == 4
    assert result["salary_count"] == 2
    assert result["median_salary"] == 102200
    assert result["salary_coverage"] == 50
    assert result["remote_share"] == 50


def test_skill_counts_once_per_job_and_denominator(jobs):
    demand = skill_demand(jobs).set_index("skill")
    assert demand.loc["Java", "jobs"] == 1
    assert demand.loc["SQL", "jobs"] == 2
    assert demand.loc["JavaScript", "share_pct"] == 50
    assert demand.share_pct.sum() > 100


def test_skill_scope_includes_nonlanguages_only_when_requested(jobs):
    jobs.at[0, "skill_tokens"] = ("Python", "Docker")
    assert "Docker" not in skill_demand(jobs).skill.tolist()
    assert "Docker" in skill_demand(jobs, languages_only=False).skill.tolist()


@pytest.mark.parametrize("options,expected", [
    (Filters(languages=("Java",)), ["B"]),
    (Filters(languages=("Python", "JavaScript"), match_all=True), ["D"]),
    (Filters(languages=("Python", "JavaScript")), ["A", "C", "D"]),
    (Filters(query="frontend"), ["C"]),
    (Filters(query=".*"), []),
    (Filters(locations=("Rockville, MD",)), ["B"]),
    (Filters(work_modes=("Remote",), levels=("Entry",)), ["A", "D"]),
    (Filters(min_salary=100000, include_missing_salary=False), ["B"]),
    (Filters(min_salary=100000), ["B", "C", "D"]),
    (Filters(min_salary=90000, include_missing_salary=False), ["A", "B"]),
    (Filters(date_start=date(2026, 10, 15), date_end=date(2026, 10, 15), include_undated=False), ["B"]),
    (Filters(date_start=date(2026, 10, 15)), ["B", "C", "D"]),
])
def test_filter_semantics(jobs, options, expected):
    assert filter_jobs(jobs, options).job_id.tolist() == expected


def test_grouped_counts_and_pay(jobs):
    groups = grouped_summary(jobs, "location").set_index("location")
    assert groups.loc["Seattle, WA", "jobs"] == 3
    assert groups.loc["Seattle, WA", "salary_count"] == 1
    assert groups.loc["Seattle, WA", "median_salary"] == 90000
    with pytest.raises(ValueError):
        grouped_summary(jobs, "company")


def test_posting_activity_includes_zero_weeks(jobs):
    activity = posting_activity(jobs)
    assert activity.jobs.tolist() == [1, 0, 2]
    assert activity.week.iloc[0] == pd.Timestamp("2026-09-28")


def test_empty_results_are_defined(jobs):
    empty = jobs.iloc[:0]
    assert summary(empty)["median_salary"] is None
    assert summary(empty)["salary_coverage"] == 0
    assert skill_demand(empty).empty
    assert grouped_summary(empty, "location").empty
    assert posting_activity(empty).empty
    assert filter_jobs(empty, Filters(languages=("Java",))).empty
    assert pd.read_csv(BytesIO(export_jobs(empty))).empty


def test_missing_salary_not_zero(jobs):
    assert summary(jobs.loc[[2, 3]])["median_salary"] is None


def test_download_is_valid_csv_with_provenance(jobs):
    output = export_jobs(jobs)
    frame = pd.read_csv(BytesIO(output), keep_default_na=False)
    assert len(frame) == 4
    assert frame.loc[2, "company"] == "'=Example"
    assert frame.loc[2, "posted_date"] == ""
    assert frame.loc[0, "data_source"] == "Synthetic test fixture"
    assert len(load_csv(output).jobs) == 4


@pytest.mark.parametrize("value", ["=1+1", "+1+1", "-1+1", "@SUM(A1)", "  =1+1", "\tvalue", "\rvalue", "\nvalue"])
def test_csv_formula_prefixes_are_escaped(value):
    raw = safe_csv(pd.DataFrame({"text": [value], "number": [90000]}))
    result = pd.read_csv(BytesIO(raw), keep_default_na=False)
    assert result.text.iloc[0].startswith("'")
    assert result.number.iloc[0] == 90000
