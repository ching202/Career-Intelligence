from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from career_intelligence import data
from career_intelligence.data import DataValidationError, clean_jobs, load_csv, parse_skills


def encoded(rows):
    return pd.DataFrame(rows).to_csv(index=False).encode()


def test_sample_has_provenance_and_unique_rows():
    result = load_csv(Path(__file__).resolve().parents[1] / "data" / "sample_jobs.csv")
    assert result.input_rows == 300
    assert len(result.jobs) == 300
    assert result.jobs.job_id.is_unique
    assert result.jobs.data_source.str.contains("Synthetic sample").all()
    assert result.jobs.salary_mid_usd.notna().sum() == 262


@pytest.mark.parametrize("raw, expected", [
    ("js;Java;JS;javaScript", ("Java", "JavaScript")),
    ("C++;C#;C;cpp;csharp", ("C", "C#", "C++")),
    ("golang | py, SQL;Python", ("Go", "Python", "SQL")),
    ("", ()),
    ("React;react.js;SomeTool;sometool", ("React", "SomeTool")),
])
def test_skills_are_exact_deduplicated_tokens(raw, expected):
    assert parse_skills(raw) == expected


@pytest.mark.parametrize("period,low,high,expected", [
    ("annual", "80000", "100000", 90000),
    ("hourly", "40", "60", 104000),
    ("weekly", "1000", "2000", 78000),
    ("monthly", "8000", "10000", 108000),
    ("yearly", "80000", "80000", 80000),
])
def test_salary_annualization(row, period, low, high, expected):
    result = load_csv(encoded([dict(row, salary_period=period, salary_min=low, salary_max=high)]))
    assert result.jobs.salary_mid_usd.iloc[0] == pytest.approx(expected)


@pytest.mark.parametrize("changes,status", [
    ({"salary_min": "", "salary_max": ""}, "Missing salary"),
    ({"salary_min": "90000", "salary_max": "80000"}, "Invalid salary"),
    ({"salary_min": "-1"}, "Invalid salary"),
    ({"salary_min": "0"}, "Invalid salary"),
    ({"salary_min": "abc"}, "Invalid salary"),
    ({"salary_max": ""}, "Invalid salary"),
    ({"salary_max": "inf"}, "Invalid salary"),
    ({"salary_min": "1e308", "salary_max": "1e308", "salary_period": "hourly"}, "Invalid salary"),
    ({"salary_currency": "EUR"}, "Unsupported currency"),
    ({"salary_period": "daily"}, "Unknown pay period"),
])
def test_unusable_pay_does_not_remove_jobs(row, changes, status):
    result = load_csv(encoded([dict(row, **changes)]))
    assert len(result.jobs) == 1
    assert result.jobs.salary_status.iloc[0] == status
    assert pd.isna(result.jobs.salary_mid_usd.iloc[0])
    assert status in result.issues.issue.tolist()


def test_drop_missing_identity_and_duplicates_keep_first(row):
    result = load_csv(encoded([row, dict(row, salary_min="999"), dict(row, job_id="B", title=""),
                               dict(row, job_id="C", location="")]))
    assert result.input_rows == 4 and result.dropped_rows == 3
    assert result.jobs.job_id.tolist() == ["A"]
    assert result.jobs.salary_mid_usd.iloc[0] == 90000
    assert set(result.issues.csv_record) == {3, 4, 5}


def test_whitespace_headers_bom_and_categories(row):
    raw = encoded([dict(row, work_mode=" on site ", experience_level="junior", salary_currency="usd")])
    raw = raw.replace(b"job_id,", b" JOB_ID ,", 1)
    result = load_csv(b"\xef\xbb\xbf" + raw)
    assert result.jobs.work_mode.iloc[0] == "On-site"
    assert result.jobs.experience_level.iloc[0] == "Entry"
    assert result.jobs.salary_mid_usd.iloc[0] == 90000


def test_unknown_categories_and_bad_dates_reported(row):
    result = load_csv(encoded([dict(row, work_mode="planet", experience_level="expert", posted_date="2026-02-30", skills="")]))
    assert result.jobs.work_mode.iloc[0] == "Unknown"
    assert result.jobs.experience_level.iloc[0] == "Unknown"
    assert pd.isna(result.jobs.posted_date.iloc[0])
    assert len(result.issues) == 4


@pytest.mark.parametrize("value", ["10/01/2026", "2026-1-1", "2026-10-01T12:00:00Z", "not a date"])
def test_dates_require_iso_calendar_day(row, value):
    assert pd.isna(load_csv(encoded([dict(row, posted_date=value)])).jobs.posted_date.iloc[0])


@pytest.mark.parametrize("raw, message", [
    (b"", "empty"), (b"hello,world\na,b", "Missing required"),
    (b"job_id,job_id\nA,B", "unique"), (b"\xff", "UTF-8"), (b"a\x00", "binary"),
])
def test_invalid_file_errors_are_useful(raw, message):
    with pytest.raises(DataValidationError, match=message):
        load_csv(raw)


def test_header_without_rows_rejected(row):
    raw = pd.DataFrame([row]).head(0).to_csv(index=False).encode()
    with pytest.raises(DataValidationError, match="no job rows"):
        load_csv(raw)


@pytest.mark.parametrize("suffix", [b"\na,b\n", b'\n"unterminated'])
def test_malformed_csv_rejected(row, suffix):
    with pytest.raises(DataValidationError):
        load_csv(encoded([row]).rstrip() + suffix)


def test_limits_apply_to_bytes_and_paths(row, tmp_path, monkeypatch):
    raw = encoded([row])
    monkeypatch.setattr(data, "MAX_BYTES", len(raw) - 1)
    path = tmp_path / "jobs.csv"
    path.write_bytes(raw)
    for value in [raw, path]:
        with pytest.raises(DataValidationError, match="10 MiB"):
            load_csv(value)


def test_row_limit(row, monkeypatch):
    monkeypatch.setattr(data, "MAX_ROWS", 1)
    with pytest.raises(DataValidationError, match="row limit"):
        load_csv(encoded([row, dict(row, job_id="B")]))


def test_all_rows_invalid_returns_typed_empty_frame(row):
    result = load_csv(encoded([dict(row, job_id="")]))
    assert result.jobs.empty and result.dropped_rows == 1
    assert "salary_mid_usd" in result.jobs.columns


def test_clean_jobs_does_not_mutate_input_and_checks_schema(row):
    frame = pd.DataFrame([row])
    original = frame.copy(deep=True)
    clean_jobs(frame)
    pd.testing.assert_frame_equal(frame, original)
    with pytest.raises(DataValidationError, match="Missing required"):
        clean_jobs(pd.DataFrame({"title": ["Developer"]}))
