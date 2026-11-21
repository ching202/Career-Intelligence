# Career Intelligence

**A free Python dashboard for exploring software developer job data.**

Career Intelligence makes it easy to compare salary ranges, language mentions, and job locations, then inspect the records behind each chart. Built for Kyle Kitching's instructor-approved AD450 practicum at North Seattle College.

> **The included 300-row dataset is entirely synthetic.** Companies, vacancies, salaries, and posting dates are fictional. Results demonstrate the software and must not be presented as findings about the real job market. Upload a properly sourced CSV to analyze a real dataset.

## What it does

- Filters jobs by title/company, location, work arrangement, experience, languages, salary, and posting date.
- Compares median annualized salary midpoints with an explicit sample size and salary coverage.
- Shows salary coverage within each experience level and location, including location CSV exports.
- Counts exact language/SQL mentions once per job; distinguishes Java from JavaScript and C from C++/C#.
- Visualizes location counts, work arrangements, experience levels, salary distributions, and posting activity.
- Imports UTF-8 CSVs, reports data-quality issues, and exports filtered records and summaries.
- Runs locally without accounts, API keys, subscriptions, scraping, or a database.

## Quick start on Windows

Install **Python 3.12**, extract this entire project folder, and open PowerShell in that folder. Run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) if a browser does not open automatically. Leave the terminal open while using the app; press **Ctrl+C** to stop it.

Alternatively, double-click `START_WINDOWS.bat` after installing Python 3.12. It creates a local environment, installs the runtime dependencies if needed, and launches the app. The launcher is provided for convenience; it has not been executed on Windows in this build session.

No PowerShell activation or execution-policy change is required. The first install needs internet access; the bundled data and dashboard then work offline. A normal laptop is sufficient; no GPU is used. A phone can download/review the project, but a desktop or laptop is needed for this local setup.

### macOS / Linux

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m streamlit run app.py
```

## Try it in two minutes

1. Keep **Sample data** selected and read the sample-data notice.
2. Select **Remote** under Work arrangement and **Python** under Languages / SQL.
3. Compare the Salaries, Languages, and Locations tabs. All charts follow the same filters.
4. Enter a minimum annual midpoint. Uncheck **Include jobs without usable USD salaries** for a strict pay filter.
5. Inspect **Explore data** and download the filtered CSV.
6. Expand **Data quality & calculation notes** to see exclusions and assumptions.
7. Click **Reset filters**, then try **Upload CSV** with the included dataset or a file matching the CSV template.

## Testing and evidence

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/verify.py
```

On macOS/Linux, substitute `.venv/bin/python`. `verify.py` saves actual console output, JUnit results, coverage, package versions, timestamps, and file hashes under `evidence/local-runs/`. It exits unsuccessfully if any check fails and never overwrites an existing evidence directory.

The initial verification result and its limits are in [evidence/README.md](evidence/README.md). The [Week 7 validation report](docs/WEEK7_VALIDATION.md) records the subsequent Windows verification, validation examples, and source publication. Automated checks use real Streamlit `AppTest` executions. Visual browser inspection and the Windows batch launcher remain separate manual checks in [TEST_PLAN.md](docs/TEST_PLAN.md). A GitHub Actions workflow is included; a remote CI run is not claimed.

## Data and calculations

The app uses pandas for validation and aggregation, Streamlit for interaction, and Plotly for charts. Salary inputs must be plain numeric bounds in the declared currency and period. Supported periods are annual, monthly, weekly, and hourly. Only USD salary ranges are compared; other jobs remain available for count and skill analysis.

**Annual midpoint = (minimum + maximum) / 2 × period factor**, where the factor is 1, 12, 52, or 2,080. The reported median is the median of valid midpoints. Missing pay is never treated as zero. The hourly factor assumes 40 hours × 52 weeks; it is an approximation, not an employment guarantee.

See the [data dictionary](docs/DATA_DICTIONARY.md), [methodology](docs/METHODOLOGY.md), and [dataset provenance](data/README.md) for the full contract and limitations.

## Project structure

| Path | Purpose |
| --- | --- |
| `app.py` | Interactive Streamlit dashboard |
| `career_intelligence/data.py` | CSV parsing, validation, normalization, quality report |
| `career_intelligence/analytics.py` | Filters, summary statistics, demand counts, exports |
| `career_intelligence/charts.py` | Plotly presentation helpers |
| `data/` | Reproducible synthetic CSV and provenance |
| `tests/` | Unit, integration, and Streamlit interaction checks |
| `scripts/` | Sample generator, verification recorder, release packager |
| `docs/milestones/` | Six milestone specifications and implementation evidence |
| `docs/weekly_updates/` | Six fill-in practicum reports for Weeks 6–11 |
| `evidence/` | Actual build/test records and Git history |
| `.github/workflows/tests.yml` | CI configuration for Python 3.11–3.13 |

## Practicum documentation

The [Week 8 analytics report](docs/WEEK8_ANALYTICS.md) documents the grouped salary-coverage improvement and a seven-job synthetic example for salary annualization, exact skill counting, and filtered denominators.

[The six-milestone plan](docs/MILESTONES.md) maps work to Weeks 6–11. These are organizational milestones, **not a claim that development happened over six weeks**. The initial implementation was prepared with an AI assistant in the recorded build session. Student dates, hours, personal contributions, reflections, and submission status remain blank until actually completed.

Use [weekly update templates](docs/weekly_updates/README.md) to record the work you personally do. Report assistance according to course requirements. Do not convert automated execution time into student work hours or backdate commits.

## GitHub and development

Source is published at [ching202/Career-Intelligence](https://github.com/ching202/Career-Intelligence). The main branch contains the initial dashboard; the [Week 7 branch](https://github.com/ching202/Career-Intelligence/tree/week7-data-validation) adds validation evidence and a line-ending fix. See [PUBLICATION.md](docs/PUBLICATION.md) for dates and Git-history provenance. [GITHUB_SETUP.md](docs/GITHUB_SETUP.md) preserves the original package's publishing instructions. Never upload the ZIP as the only repository file; GitHub should show `app.py`, `README.md`, `data/`, and the other project files at the top level.

Use small, meaningful commits for future changes, run the affected tests, and add evidence when a feature is verified. See [ARCHITECTURE.md](docs/ARCHITECTURE.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## Scope and limitations

This is a descriptive analytics MVP, not a job board, salary predictor, or application system. It does not infer skills from descriptions, track hiring outcomes, scrape vacancies, geocode locations, or correct selection bias. CSVs are limited to 10 MiB and 50,000 records. Uploads are processed in memory and are not saved by the app; downloaded files are under the user's control. The default server binds only to the local machine.

## License and references

Source code and generated sample data are released under the [MIT License](LICENSE). Third-party libraries retain their own licenses.

- [Python virtual environments](https://docs.python.org/3/library/venv.html)
- [pandas documentation](https://pandas.pydata.org/docs/)
- [Streamlit documentation](https://docs.streamlit.io/)
- [Streamlit app testing](https://docs.streamlit.io/develop/concepts/app-testing)
- [Plotly Python documentation](https://plotly.com/python/)
- [pytest documentation](https://docs.pytest.org/)

These are implementation references, not sources for real salary or demand findings.
