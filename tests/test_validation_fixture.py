"""End-to-end expectations for the documented mixed-quality CSV example."""
from pathlib import Path

import pandas as pd
import pytest

from career_intelligence.analytics import export_jobs, summary
from career_intelligence.data import DataValidationError, load_csv

FIXTURE = Path(__file__).parent / 'fixtures' / 'validation_cases.csv'


def test_mixed_quality_fixture_keeps_countable_jobs_and_audits_original_rows():
    dataset = load_csv(FIXTURE)
    assert (dataset.input_rows, dataset.dropped_rows) == (7, 2)
    assert dataset.jobs.job_id.tolist() == [
        'VALID-1', 'NO-PAY', 'BAD-DATE', 'NON-USD', 'BAD-RANGE'
    ]
    assert dataset.jobs.set_index('job_id').loc['VALID-1', 'salary_mid_usd'] == 90000
    assert set(dataset.issues[['csv_record', 'issue']].itertuples(index=False, name=None)) == {
        (3, 'Duplicate job_id'),
        (4, 'Missing salary'),
        (5, 'Missing or invalid posted_date'),
        (6, 'Missing job_id, title, or location'),
        (7, 'Unsupported currency'),
        (8, 'Invalid salary'),
    }
    stats = summary(dataset.jobs)
    assert stats['jobs'] == 5
    assert stats['salary_count'] == 2
    assert stats['salary_coverage'] == 40
    assert stats['median_salary'] == 100000


def test_cleaned_fixture_export_reimports_without_changing_retained_jobs():
    first = load_csv(FIXTURE)
    exported = export_jobs(first.jobs)
    second = load_csv(exported)
    assert second.input_rows == 5 and second.dropped_rows == 0
    assert first.jobs.job_id.tolist() == second.jobs.job_id.tolist()
    pd.testing.assert_series_equal(first.jobs.salary_mid_usd, second.jobs.salary_mid_usd)
    assert second.jobs.data_source.eq('Synthetic validation fixture').all()
    assert pd.isna(second.jobs.set_index('job_id').loc['BAD-DATE', 'posted_date'])


def test_missing_column_reports_the_specific_required_header():
    frame = pd.read_csv(FIXTURE, dtype=str, keep_default_na=False).drop(columns=['skills'])
    with pytest.raises(DataValidationError, match='Missing required columns: skills'):
        load_csv(frame.to_csv(index=False).encode('utf-8'))
