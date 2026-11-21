"""Worked salary, skill, and location examples through the real CSV pipeline."""

from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from career_intelligence.analytics import Filters, filter_jobs, grouped_summary, safe_csv, skill_demand, summary
from career_intelligence.data import load_csv

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/analytics_cases.csv"


@pytest.fixture
def analytics_jobs():
    return load_csv(FIXTURE).jobs


@pytest.mark.parametrize("job_id, expected", [
    ("ANNUAL", 90000), ("MONTHLY", 108000),
    ("HOURLY", 114400), ("WEEKLY", 91000),
])
def test_worked_pay_period_midpoints(analytics_jobs, job_id, expected):
    assert analytics_jobs.set_index("job_id").loc[job_id, "salary_mid_usd"] == expected


def test_worked_overall_median_and_coverage(analytics_jobs):
    result = summary(analytics_jobs)
    assert result["jobs"] == 7
    assert result["salary_count"] == 5
    assert result["median_salary"] == 100000
    assert result["salary_coverage"] == pytest.approx(500 / 7)
    assert result["remote_share"] == pytest.approx(400 / 7)


def test_skill_counts_keep_unskilled_jobs_in_denominator(analytics_jobs):
    result = skill_demand(analytics_jobs).set_index("skill")
    assert result.jobs.to_dict() == {"JavaScript": 3, "Python": 3, "SQL": 2, "C": 1, "C#": 1, "C++": 1, "Java": 1}
    assert result.loc["Java", "share_pct"] == pytest.approx(100 / 7)
    assert result.loc["JavaScript", "share_pct"] == pytest.approx(300 / 7)
    assert result.share_pct.sum() == pytest.approx(1200 / 7)


def test_exact_tokens_do_not_mix_java_or_c_variants(analytics_jobs):
    assert filter_jobs(analytics_jobs, Filters(languages=("Java",))).job_id.tolist() == ["ANNUAL"]
    assert filter_jobs(analytics_jobs, Filters(languages=("JavaScript",))).job_id.tolist() == ["MONTHLY", "HOURLY", "CAD"]
    systems = analytics_jobs.set_index("job_id").loc["WEEKLY", "skill_tokens"]
    assert set(systems) == {"C", "C++", "C#"}
    assert filter_jobs(analytics_jobs, Filters(languages=("C", "C++", "C#"), match_all=True)).job_id.tolist() == ["WEEKLY"]


@pytest.mark.parametrize("group, expected", [
    ("location", {"Seattle, WA": (3, 2, 99000, 200 / 3), "Portland, OR": (2, 2, 102700, 100), "Toronto, ON": (2, 1, 100000, 50)}),
    ("work_mode", {"Remote": (4, 2, 102200, 50), "Hybrid": (1, 1, 108000, 100), "On-site": (2, 2, 95500, 100)}),
    ("experience_level", {"Entry": (3, 2, 95000, 200 / 3), "Mid": (2, 2, 99500, 100), "Senior": (2, 1, 114400, 50)}),
])
def test_group_metrics_match_worked_examples(analytics_jobs, group, expected):
    result = grouped_summary(analytics_jobs, group).set_index(group)
    assert set(result.index) == set(expected)
    for label, values in expected.items():
        assert tuple(result.loc[label, ["jobs", "salary_count", "median_salary", "salary_coverage"]]) == pytest.approx(values)


def test_shared_filters_recalculate_group_and_skill_denominators(analytics_jobs):
    filtered = filter_jobs(analytics_jobs, Filters(locations=("Seattle, WA",), work_modes=("Remote",)))
    assert filtered.job_id.tolist() == ["ANNUAL", "MISSING"]
    group = grouped_summary(filtered, "location").iloc[0]
    assert (group.jobs, group.salary_count, group.median_salary, group.salary_coverage) == (2, 1, 90000, 50)
    assert skill_demand(filtered).share_pct.tolist() == [50, 50, 50]


def test_group_without_usable_salary_shows_zero_coverage_not_zero_pay(analytics_jobs):
    filtered = filter_jobs(analytics_jobs, Filters(query="Missing salary"))
    group = grouped_summary(filtered, "location").iloc[0]
    assert group.jobs == 1 and group.salary_count == 0 and group.salary_coverage == 0
    assert pd.isna(group.median_salary)


@pytest.mark.parametrize("group", ["location", "work_mode", "experience_level"])
def test_empty_grouped_summary_keeps_export_columns(analytics_jobs, group):
    result = grouped_summary(analytics_jobs.iloc[:0], group)
    assert result.empty
    assert result.columns.tolist() == [group, "jobs", "salary_count", "median_salary", "salary_coverage"]


def test_location_download_preserves_numeric_coverage(analytics_jobs):
    raw = safe_csv(grouped_summary(analytics_jobs, "location"))
    downloaded = pd.read_csv(BytesIO(raw)).set_index("location")
    assert downloaded.loc["Seattle, WA", "salary_coverage"] == pytest.approx(200 / 3)
    assert downloaded.loc["Toronto, ON", "salary_count"] == 1


def test_dashboard_group_tables_recalculate_coverage_after_filters(monkeypatch):
    monkeypatch.setattr("streamlit.file_uploader", lambda *args, **kwargs: BytesIO(FIXTURE.read_bytes()))
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    app.radio(key="data_source").set_value("Upload CSV").run()
    assert not app.exception
    locations = next(item.value for item in app.dataframe if {"location", "salary_coverage"} <= set(item.value.columns))
    experience = next(item.value for item in app.dataframe if {"experience_level", "salary_coverage"} <= set(item.value.columns))
    assert locations.set_index("location").loc["Seattle, WA", "salary_coverage"] == pytest.approx(200 / 3)
    assert experience.set_index("experience_level").loc["Senior", "salary_coverage"] == 50
    app.multiselect(key="filter_locations").set_value(["Seattle, WA"])
    app.multiselect(key="filter_modes").set_value(["Remote"]).run()
    assert not app.exception
    locations = next(item.value for item in app.dataframe if {"location", "salary_coverage"} <= set(item.value.columns))
    assert locations.salary_coverage.tolist() == [50]
    assert app.metric[2].value == "50.0%"
