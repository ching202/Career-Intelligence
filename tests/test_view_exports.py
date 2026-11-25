"""Exercise the downloaded view against real filtering and dashboard state."""

import json
from datetime import date
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from career_intelligence.analytics import Filters, filter_jobs
from career_intelligence.data import load_csv
from career_intelligence.exports import export_view_bundle

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/analytics_cases.csv"


def unpack(payload):
    with ZipFile(BytesIO(payload)) as archive:
        assert set(archive.namelist()) == {"filtered_jobs.csv", "language_demand.csv", "location_summary.csv", "view_summary.json"}
        assert archive.testzip() is None
        frames = {name: pd.read_csv(BytesIO(archive.read(name))) for name in archive.namelist() if name.endswith(".csv")}
        context = json.loads(archive.read("view_summary.json"))
    return frames, context


def test_view_bundle_matches_combined_filters_and_provenance():
    raw = FIXTURE.read_bytes()
    jobs = load_csv(raw).jobs
    filters = Filters(locations=("Seattle, WA",), work_modes=("Remote",))
    frames, context = unpack(export_view_bundle(filter_jobs(jobs, filters), filters,
        dataset_sha256=sha256(raw).hexdigest(), validated_jobs=len(jobs)))
    assert frames["filtered_jobs.csv"].job_id.tolist() == ["ANNUAL", "MISSING"]
    assert frames["filtered_jobs.csv"].data_source.eq("Synthetic Week 8 analytics fixture").all()
    assert context["dataset_sha256"] == sha256(raw).hexdigest()
    assert context["validated_jobs"] == 7 and context["summary"]["jobs"] == 2
    assert context["summary"]["median_salary"] == 90000
    assert context["summary"]["salary_coverage"] == 50
    assert context["filters"]["locations"] == ["Seattle, WA"]
    assert frames["location_summary.csv"].salary_coverage.tolist() == [50]
    assert frames["language_demand.csv"].share_pct.tolist() == [50, 50, 50]


@pytest.mark.parametrize("languages_only, expected", [(True, {"Python"}), (False, {"Python", "Docker"})])
def test_bundle_respects_language_scope(row, languages_only, expected):
    raw = pd.DataFrame([dict(row, skills="Python;Docker;Docker")]).to_csv(index=False).encode()
    frames, context = unpack(export_view_bundle(load_csv(raw).jobs, Filters(),
        dataset_sha256=sha256(raw).hexdigest(), validated_jobs=1, languages_only=languages_only))
    assert set(frames["language_demand.csv"].skill) == expected
    assert frames["language_demand.csv"].jobs.eq(1).all()
    assert context["language_scope"] == ("Languages and SQL" if languages_only else "All skill tokens")


def test_empty_view_exports_headers_and_null_median():
    jobs = load_csv(FIXTURE).jobs
    filters = Filters(query="no-such-job-zzzz")
    frames, context = unpack(export_view_bundle(filter_jobs(jobs, filters), filters,
        dataset_sha256=sha256(FIXTURE.read_bytes()).hexdigest(), validated_jobs=7))
    assert all(frame.empty for frame in frames.values())
    assert context["summary"]["median_salary"] is None
    assert context["summary"]["jobs"] == 0
    assert "salary_coverage" in frames["location_summary.csv"]


def test_bundle_keeps_formula_escaping_in_all_csvs(row):
    raw = pd.DataFrame([dict(row, company="=1+1", location="@City", skills="+Formula")]).to_csv(index=False).encode()
    frames, _ = unpack(export_view_bundle(load_csv(raw).jobs, Filters(),
        dataset_sha256=sha256(raw).hexdigest(), validated_jobs=1, languages_only=False))
    assert frames["filtered_jobs.csv"].company.iloc[0] == "'=1+1"
    assert frames["location_summary.csv"].location.iloc[0] == "'@City"
    assert frames["language_demand.csv"].skill.iloc[0] == "'+Formula"


def test_bundle_records_date_bounds_as_iso_dates():
    jobs = load_csv(FIXTURE).jobs
    filters = Filters(date_start=date(2026, 11, 18), date_end=date(2026, 11, 19), include_undated=False)
    frames, context = unpack(export_view_bundle(filter_jobs(jobs, filters), filters,
        dataset_sha256=sha256(FIXTURE.read_bytes()).hexdigest(), validated_jobs=7))
    assert context["filters"]["date_start"] == "2026-11-18"
    assert context["filters"]["date_end"] == "2026-11-19"
    assert frames["filtered_jobs.csv"].job_id.tolist() == ["HOURLY", "WEEKLY"]


@pytest.fixture
def dashboard(monkeypatch):
    state = {"raw": FIXTURE.read_bytes()}
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: BytesIO(state["raw"]))
    original_download = st.download_button

    def capture(label, data, *args, **kwargs):
        if label == "Download current view (ZIP)":
            state["payload"] = data
        return original_download(label, data, *args, **kwargs)

    monkeypatch.setattr(st, "download_button", capture)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    app.radio(key="data_source").set_value("Upload CSV").run()
    assert not app.exception
    return app, state


def test_dashboard_zip_matches_displayed_filtered_records(dashboard):
    app, state = dashboard
    app.multiselect(key="filter_locations").set_value(["Seattle, WA"])
    app.multiselect(key="filter_modes").set_value(["Remote"]).run()
    assert not app.exception
    frames, context = unpack(state["payload"])
    visible = next(item.value for item in app.dataframe if "title" in item.value.columns)
    assert frames["filtered_jobs.csv"].job_id.tolist() == visible.job_id.tolist() == ["ANNUAL", "MISSING"]
    assert context["summary"]["jobs"] == int(app.metric[0].value) == 2
    assert app.metric[2].value == "50.0%"


def test_dashboard_empty_view_then_reset_refreshes_archive(dashboard):
    app, state = dashboard
    app.text_input(key="filter_query").set_value("no-such-job-zzzz").run()
    assert not app.exception
    assert unpack(state["payload"])[1]["summary"]["jobs"] == 0
    app.button[0].click().run()
    assert not app.exception
    frames, context = unpack(state["payload"])
    assert context["summary"]["jobs"] == len(frames["filtered_jobs.csv"]) == 7
    assert context["filters"]["query"] == ""
    assert app.text_input(key="filter_query").proto.set_value


def test_replacing_uploaded_file_resets_filters_and_export(dashboard, row):
    app, state = dashboard
    app.text_input(key="filter_query").set_value("Missing salary").run()
    state["raw"] = pd.DataFrame([dict(row, job_id="REPLACEMENT")]).to_csv(index=False).encode()
    app.run()
    assert not app.exception
    frames, context = unpack(state["payload"])
    assert frames["filtered_jobs.csv"].job_id.tolist() == ["REPLACEMENT"]
    assert context["validated_jobs"] == context["summary"]["jobs"] == 1
    assert context["dataset_sha256"] == sha256(state["raw"]).hexdigest()
    assert context["filters"]["query"] == app.text_input(key="filter_query").value == ""
    # Verify the frontend receives an explicit update, not only a backend reset.
    assert app.text_input(key="filter_query").proto.set_value


def test_dashboard_scope_is_saved_in_current_view(dashboard):
    app, state = dashboard
    app.radio(key="demand_scope").set_value("All skill tokens").run()
    assert not app.exception
    assert unpack(state["payload"])[1]["language_scope"] == "All skill tokens"


def test_reset_restores_combined_filter_controls(dashboard):
    app, state = dashboard
    app.multiselect(key="filter_modes").set_value(["Remote"])
    app.checkbox(key="filter_missing").uncheck()
    app.checkbox(key="filter_use_date").check().run()
    assert not app.exception and len(app.date_input) == 1
    app.button[0].click().run()
    assert not app.exception
    assert app.multiselect(key="filter_modes").value == []
    assert app.checkbox(key="filter_missing").value is True
    assert app.checkbox(key="filter_use_date").value is False
    assert len(app.date_input) == 0
    assert unpack(state["payload"])[1]["summary"]["jobs"] == 7
    assert not any("Session State API" in item.value for item in app.warning)
