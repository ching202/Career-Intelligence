import pandas as pd
import pytest

from career_intelligence.data import clean_jobs


@pytest.fixture
def row():
    return dict(job_id="A", title="Backend Developer", company="Example", location="Seattle, WA",
                work_mode="Remote", experience_level="Entry", salary_min="80000", salary_max="100000",
                salary_currency="USD", salary_period="annual", skills="Python;SQL", posted_date="2026-10-01",
                data_source="Synthetic test fixture")


@pytest.fixture
def jobs(row):
    return clean_jobs(pd.DataFrame([
        row,
        dict(row, job_id="B", title="Java Developer", location="Rockville, MD", work_mode="Hybrid",
             experience_level="Mid", salary_min="50", salary_max="60", salary_period="hourly",
             skills="Java;SQL;Java", posted_date="2026-10-15"),
        dict(row, job_id="C", title="Frontend Developer", company="=Example", work_mode="On-site",
             salary_min="", salary_max="", skills="JavaScript;TypeScript", posted_date=""),
        dict(row, job_id="D", salary_currency="EUR", skills="Python;JavaScript", posted_date="2026-10-16"),
    ])).jobs
