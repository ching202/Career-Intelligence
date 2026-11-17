from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.fixture
def app():
    return AppTest.from_file(str(APP), default_timeout=30).run()


def test_default_dashboard_loads_and_labels_sample(app):
    assert not app.exception
    assert app.metric[0].value == "300"
    assert any("SAMPLE DATA" in item.value for item in app.warning)
    assert len(app.tabs) == 5
    assert len(app.get("plotly_chart")) >= 6


def test_title_filter_updates_all_record_metrics(app):
    app.text_input(key="filter_query").set_value("Backend").run()
    assert not app.exception
    assert 0 < int(app.metric[0].value) < 300
    records = next(item.value for item in app.dataframe if "title" in item.value.columns)
    assert len(records) == int(app.metric[0].value)
    assert records.title.str.contains("Backend").all()


def test_empty_filter_recovers_with_reset(app):
    app.text_input(key="filter_query").set_value("no-such-job-zzzz").run()
    assert not app.exception
    assert app.metric[0].value == "0"
    assert app.metric[1].value == "N/A"
    assert any("No jobs match" in item.value for item in app.info)
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[0].value == "300"


def test_combined_remote_and_language_filters(app):
    app.multiselect(key="filter_modes").set_value(["Remote"])
    app.multiselect(key="filter_languages").set_value(["Python"])
    app.run()
    assert not app.exception
    assert app.metric[3].value == "100.0%"
    assert 0 < int(app.metric[0].value) < 300


def test_salary_filter_excludes_unusable_when_requested(app):
    app.checkbox(key="filter_missing").uncheck()
    app.number_input(key="filter_salary").set_value(100000).run()
    assert not app.exception
    assert app.metric[2].value == "100.0%"


def test_date_range_and_demand_scope(app):
    app.checkbox(key="filter_use_date").check().run()
    assert not app.exception
    assert len(app.date_input) == 1
    app.radio(key="demand_scope").set_value("All skill tokens").run()
    assert not app.exception


def test_upload_mode_requires_a_file(app):
    app.radio(key="data_source").set_value("Upload CSV").run()
    assert not app.exception
    assert any("Choose a CSV" in item.value for item in app.info)
    assert len(app.metric) == 0


def test_uploaded_csv_recalculates_and_resets_filters(app, row, monkeypatch):
    app.text_input(key="filter_query").set_value("does not exist").run()
    raw = pd.DataFrame([dict(row, data_source="Sampled public-job test fixture")]).to_csv(index=False).encode()
    monkeypatch.setattr("streamlit.file_uploader", lambda *args, **kwargs: BytesIO(raw))
    app.radio(key="data_source").set_value("Upload CSV").run()
    assert not app.exception
    assert app.metric[0].value == "1"
    assert app.metric[1].value == "$90,000"
    assert app.text_input(key="filter_query").value == ""
    assert any("Uploaded data" in item.value for item in app.info)
    assert not any("SAMPLE DATA" in item.value for item in app.warning)


@pytest.mark.parametrize("case,message", [
    ("malformed", "Unable to load"), ("identity", "No usable jobs"),
])
def test_upload_errors_are_visible_not_tracebacks(app, row, monkeypatch, case, message):
    raw = b"bad,csv\n1,2" if case == "malformed" else pd.DataFrame([dict(row, job_id="")]).to_csv(index=False).encode()
    monkeypatch.setattr("streamlit.file_uploader", lambda *args, **kwargs: BytesIO(raw))
    app.radio(key="data_source").set_value("Upload CSV").run()
    assert not app.exception
    assert any(message in item.value for item in app.error)


def test_upload_missing_salaries_dates_and_languages(app, row, monkeypatch):
    raw = pd.DataFrame([dict(row, salary_min="", salary_max="", posted_date="", skills="Docker")]).to_csv(index=False).encode()
    monkeypatch.setattr("streamlit.file_uploader", lambda *args, **kwargs: BytesIO(raw))
    app.radio(key="data_source").set_value("Upload CSV").run()
    assert not app.exception
    assert app.metric[0].value == "1"
    assert app.metric[1].value == "N/A"
    assert any("No usable USD" in item.value for item in app.info)
    assert any("No valid posting dates" in item.value for item in app.info)
    assert any("No recognized language" in item.value for item in app.info)
    app.checkbox(key="filter_use_date").check().run()
    assert not app.exception
