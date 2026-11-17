"""Run with: python -m streamlit run app.py"""

from hashlib import sha256
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from career_intelligence.analytics import (
    Filters, export_jobs, filter_jobs, grouped_summary, posting_activity, safe_csv,
    skill_demand, summary,
)
from career_intelligence.charts import PALETTE, horizontal_bar, salary_histogram, style
from career_intelligence.data import DataValidationError, LANGUAGES, REQUIRED_COLUMNS, load_csv

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Career Intelligence", page_icon="📊", layout="wide")


def reset_filters():
    for key in list(st.session_state):
        if key.startswith("filter_"):
            del st.session_state[key]


def show_chart(figure):
    st.plotly_chart(figure, use_container_width=True, config={"displaylogo": False})


@st.cache_data(show_spinner=False)
def sample_bytes():
    return (ROOT / "data" / "sample_jobs.csv").read_bytes()


st.caption("CAREER INTELLIGENCE  /  SOFTWARE DEVELOPER JOB DATA")
st.title("Find patterns. Plan your next move.")
st.write("Explore salary ranges, language mentions, and job locations in one transparent dashboard.")

with st.sidebar:
    st.header("Your dataset")
    source = st.radio("Data source", ["Sample data", "Upload CSV"], key="data_source")
    uploaded = st.file_uploader("Choose a job CSV", type=["csv"], key="csv_upload") if source == "Upload CSV" else None
    st.download_button("Download CSV template", safe_csv(pd.DataFrame(columns=REQUIRED_COLUMNS)),
                       "career_intelligence_template.csv", "text/csv")
    st.caption("UTF-8 CSV · up to 10 MiB / 50,000 rows. The template lists all required columns.")

if source == "Upload CSV" and uploaded is None:
    st.info("Choose a CSV in the sidebar to begin, or switch back to Sample data.")
    st.stop()
try:
    raw = sample_bytes() if source == "Sample data" else uploaded.getvalue()
    dataset = load_csv(raw)
except (DataValidationError, OSError) as exc:
    st.error(f"Unable to load this dataset: {exc}")
    st.caption("Check the CSV template and docs/DATA_DICTIONARY.md, then try again.")
    st.stop()

jobs = dataset.jobs
fingerprint = sha256(raw).hexdigest()
if st.session_state.get("dataset_fingerprint") != fingerprint:
    reset_filters()
    st.session_state["dataset_fingerprint"] = fingerprint

has_sample = jobs.data_source.str.match(r"synthetic\b", case=False).any()
if source == "Sample data" or has_sample:
    st.warning("SAMPLE DATA — fictional jobs, salaries, companies, and posting dates. These charts demonstrate the app; they do not describe the real job market.")
else:
    st.info("Uploaded data — results describe only this file. Its source, completeness, and freshness have not been independently verified.")

if jobs.empty:
    st.error("No usable jobs remain after validation. Each row needs a job ID, title, and location.")
    st.dataframe(dataset.issues, hide_index=True, use_container_width=True)
    st.stop()

with st.sidebar:
    st.divider()
    st.header("Focus your view")
    st.button("Reset filters", on_click=reset_filters, use_container_width=True)
    query = st.text_input("Title or company", key="filter_query", placeholder="e.g. Backend")
    locations = st.multiselect("Locations", sorted(jobs.location.unique()), key="filter_locations")
    modes = st.multiselect("Work arrangement", sorted(jobs.work_mode.unique()), key="filter_modes")
    levels = st.multiselect("Experience level", sorted(jobs.experience_level.unique()), key="filter_levels")
    available_languages = sorted(set().union(*jobs.skill_tokens) & LANGUAGES)
    languages = st.multiselect("Languages / SQL", available_languages, key="filter_languages")
    match = st.radio("Language matching", ["Any selected", "All selected"], horizontal=True, key="filter_match")
    minimum = st.number_input("Minimum annual midpoint (USD)", min_value=0, max_value=10000000,
                              step=5000, key="filter_salary")
    include_missing = st.checkbox("Include jobs without usable USD salaries", value=True, key="filter_missing")
    st.caption("When checked, jobs without comparable pay remain visible even with a minimum salary set.")
    date_start = date_end = None
    include_undated = True
    if st.checkbox("Filter by posting date", key="filter_use_date"):
        dated = jobs.posted_date.dropna()
        if dated.empty:
            st.caption("This dataset has no usable posting dates.")
        else:
            selected_dates = st.date_input("Posting date range", value=(dated.min().date(), dated.max().date()),
                                           min_value=dated.min().date(), max_value=dated.max().date(),
                                           key="filter_dates")
            if len(selected_dates) == 2:
                date_start, date_end = selected_dates
            else:
                st.caption("Select both dates to apply the range.")
            include_undated = st.checkbox("Include jobs without dates", value=True, key="filter_undated")

filtered = filter_jobs(jobs, Filters(
    query=query, locations=tuple(locations), work_modes=tuple(modes), levels=tuple(levels),
    languages=tuple(languages), match_all=match == "All selected", min_salary=minimum,
    include_missing_salary=include_missing, date_start=date_start, date_end=date_end,
    include_undated=include_undated,
))
metrics = summary(filtered)
st.caption(f"Showing {len(filtered):,} of {len(jobs):,} validated job records · All charts follow the sidebar filters")
cols = st.columns(4)
cols[0].metric("Job records", f"{metrics['jobs']:,}")
cols[1].metric("Median annual midpoint", f"${metrics['median_salary']:,.0f}" if metrics["median_salary"] is not None else "N/A")
cols[2].metric("Usable USD salary coverage", f"{metrics['salary_coverage']:.1f}%")
cols[3].metric("Remote share", f"{metrics['remote_share']:.1f}%")
st.caption(f"Salary calculations use {metrics['salary_count']:,} records. Hourly × 2,080; weekly × 52; monthly × 12. No currency conversion.")

overview, salaries, demand, locations_tab, explorer = st.tabs(["Overview", "Salaries", "Languages", "Locations", "Explore data"])
if filtered.empty:
    st.info("No jobs match these filters. Try fewer selections or use Reset filters.")
else:
    with overview:
        left, right = st.columns(2)
        with left:
            st.subheader("Where work happens")
            mode_summary = grouped_summary(filtered, "work_mode")
            show_chart(horizontal_bar(mode_summary, "work_mode", "jobs", "Job records"))
        with right:
            st.subheader("Experience mix")
            show_chart(horizontal_bar(grouped_summary(filtered, "experience_level"), "experience_level", "jobs", "Job records"))
        st.subheader("Posting activity in this dataset")
        activity = posting_activity(filtered)
        if activity.empty:
            st.info("No valid posting dates are available for this view.")
        else:
            fig = px.line(activity, x="week", y="jobs", markers=True, color_discrete_sequence=PALETTE)
            fig.update_layout(xaxis_title="Week beginning Monday", yaxis_title="Job records")
            show_chart(style(fig))
        st.caption("Posting counts are a snapshot of this file, not a measure of market growth. Missing dates are omitted; weeks at the edges may be incomplete.")
    with salaries:
        st.subheader("Salary distribution")
        st.write("Each record contributes the midpoint of its stated range, converted to annual USD only when comparable.")
        if metrics["salary_count"]:
            show_chart(salary_histogram(filtered))
            st.subheader("Compare experience levels")
            grouped = grouped_summary(filtered, "experience_level")
            show_chart(horizontal_bar(grouped.dropna(subset=["median_salary"]), "experience_level", "median_salary",
                                      "Median annual midpoint (USD)", {"salary_count": True, "jobs": True}))
            st.dataframe(grouped, hide_index=True, use_container_width=True,
                         column_config={"median_salary": st.column_config.NumberColumn("Median annual USD", format="$%.0f")})
        else:
            st.info("No usable USD salary ranges remain. Job counts and language/location analysis still work.")
        st.caption("Midpoints are advertised/example compensation, not actual earnings. Benefits, equity, bonuses, taxes, cost of living, and exchange rates are not modeled.")
    with demand:
        st.subheader("Language mentions")
        scope = st.radio("Count", ["Languages and SQL", "All skill tokens"], horizontal=True, key="demand_scope")
        demand_frame = skill_demand(filtered, languages_only=scope == "Languages and SQL")
        if demand_frame.empty:
            st.info("No recognized language tokens are present in this view. Try All skill tokens.")
        else:
            show_chart(horizontal_bar(demand_frame.head(15), "skill", "jobs", "Jobs mentioning the skill", {"share_pct": ":.1f"}))
            st.dataframe(demand_frame, hide_index=True, use_container_width=True,
                         column_config={"share_pct": st.column_config.NumberColumn("Share of filtered jobs (%)", format="%.1f")})
            st.download_button("Download demand summary", safe_csv(demand_frame), "language_demand.csv", "text/csv")
        st.caption("One mention per job per skill. Percentages use all filtered jobs and may add to more than 100%. SQL is included as a query language. Counts are sample/file frequency, not a labor-market demand estimate.")
    with locations_tab:
        st.subheader("Locations represented")
        by_location = grouped_summary(filtered, "location")
        show_chart(horizontal_bar(by_location.head(15), "location", "jobs", "Job records", {"salary_count": True}))
        st.dataframe(by_location, hide_index=True, use_container_width=True,
                     column_config={"median_salary": st.column_config.NumberColumn("Median annual USD", format="$%.0f")})
        st.caption("Location labels are taken from the CSV. Remote is a work arrangement; a remote job can still have a geographic location or eligibility restriction.")
        st.download_button("Download location summary", safe_csv(by_location), "location_summary.csv", "text/csv")
    with explorer:
        st.subheader("Inspect the records behind the charts")
        visible = filtered[["job_id", "title", "company", "location", "work_mode", "experience_level",
                            "salary_mid_usd", "salary_status", "skills", "posted_date", "data_source"]]
        st.dataframe(visible, hide_index=True, use_container_width=True,
                     column_config={"salary_mid_usd": st.column_config.NumberColumn("Annual midpoint USD", format="$%.0f")})

st.download_button("Download filtered jobs", export_jobs(filtered), "career_intelligence_filtered.csv", "text/csv", type="primary")
with st.expander("Data quality & calculation notes"):
    st.write(f"Input: {dataset.input_rows:,} rows · Retained: {len(jobs):,} · Dropped: {dataset.dropped_rows:,}")
    st.caption("Quality notes cover the full loaded file. A row can have several notes. Missing or invalid salaries stay in job counts but are excluded from salary statistics.")
    if dataset.issues.empty:
        st.success("No validation issues were found.")
    else:
        st.dataframe(dataset.issues, hide_index=True, use_container_width=True)
        st.download_button("Download quality report", safe_csv(dataset.issues), "data_quality.csv", "text/csv")
    st.markdown("**Method:** median of valid annualized range midpoints; exact normalized skill tokens; one row per job ID; no salary imputation. Duplicate IDs keep the first row with a usable identity.")
    st.caption("CSV exports escape spreadsheet formula prefixes. Uploads are processed in memory and are not written to disk by the app.")
st.divider()
st.caption("Career Intelligence · AD450 practicum · North Seattle College · Free, open-source Python")
