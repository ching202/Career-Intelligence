# Week 9: interactive dashboard and exports

Technical work and publication date: **November 24, 2026**. Career Intelligence's Week 9 update was prepared with OpenAI Codex assistance. Examples use the existing synthetic fixtures, not real job-market data.

## Download the complete displayed view

Added **Save this view → Download current view (ZIP)**. The download packages:

| File | Contents |
| --- | --- |
| `filtered_jobs.csv` | Selected jobs, salary calculations, and original source labels |
| `language_demand.csv` | Language/skill frequencies using the selected scope |
| `location_summary.csv` | Group counts, salary medians, and salary coverage |
| `view_summary.json` | Active filters, dashboard metrics, input-file hash, skill scope, and export timestamp |

The original full input file is not included. ZIP generation stays in memory, CSV formula-prefix escaping remains in place, and empty views still export usable headers with a zero-job summary. JSON settings are an audit record, not an automatic import/restore feature.

Implementation: [exports.py](../career_intelligence/exports.py) and [app.py](../app.py). Reproduction: `python scripts/record_view_example.py --output evidence/local-runs/week9-example` with the pinned project environment. Use a new output directory for each run.

## Browser-discovered reset bug and fix

During an actual browser test, replacing an uploaded CSV reset the calculated results but left **Missing salary** visible in the search box. Deleting the widget's session-state key did not reliably clear its frontend value. This could make displayed filters disagree with displayed results.

Reset now assigns explicit default values to existing filter controls, while removing dependent date selections. True-by-default salary/date checkboxes initialize their values through session state without duplicate-default warnings. The affected browser checks were repeated after the fix: replacing the CSV and pressing Reset both cleared the visible search text and restored the current dataset's records.

The regression tests now check that an explicit frontend value update is sent, in addition to checking the backend results. This illustrates why a passing application test suite does not replace browser verification.

## Actual browser observations

The in-app browser connected to the local Streamlit server. Files were selected through its real file chooser and the new ZIP was saved through its download control.

| Scenario | Observed result |
| --- | --- |
| Initial synthetic sample | 300 job records |
| Upload `analytics_cases.csv` | 7 jobs; $100,000 median; 71.4% salary coverage |
| Seattle + Remote | 2 jobs; $90,000 median; 50.0% salary coverage; 100.0% remote |
| Dashboard navigation | Overview, Salaries, Languages, Locations, and Explore data opened |
| Download the filtered ZIP | Four expected files; ANNUAL and MISSING were the only exported jobs |
| No-match search and Reset | No-results message followed by recovery to the current full dataset |
| Replace the upload with `validation_cases.csv` after the fix | 5 validated jobs; 40.0% salary coverage; visibly empty search field |

The downloaded ZIP's SHA-256 is `29a3c2a84615f3dfe1669b9a89a6886fad3d1bb67d2633a5bed4f02e49b2993b`. Its extracted JSON preserves Seattle/Remote filters and the same two-job metrics shown in the dashboard.

- [Browser check record](../evidence/week9-browser/browser-checks.json)
- [Actual browser-downloaded ZIP](../evidence/week9-browser/downloaded_view.zip)
- [Extracted records](../evidence/week9-browser/filtered_jobs.csv)
- [Extracted settings and metrics](../evidence/week9-browser/view_summary.json)
- [Filtered records and download controls](../evidence/week9-browser/filtered-view.jpg)
- [Filtered location view](../evidence/week9-browser/filtered-locations.jpg)
- [Fixed reset behavior](../evidence/week9-browser/replacement-reset.jpg)

The separate [generated export example](../evidence/week9-export-example) was created programmatically; it is labeled separately from the real browser download.

## Automated verification and limits

[New regression tests](../tests/test_view_exports.py) cover combined filters, scope selection, provenance, date settings, formula escaping, empty exports, reset, dataset replacement, and consistent visible/exported results.

The final run passed **111 tests** with no failures, errors, or skips and **99.4% combined statement/branch coverage**. The dependency check also passed. Eleven new cases cover this milestone. The [final verification directory](../evidence/week9-final-verification) contains actual commands, timestamps, source hashes, dependency checks, JUnit results, console output, and coverage. The earlier `week9-verification` directory preserves the 110-test run before the browser-discovered reset fix; it is not the final result.

Browser checks cover the local in-app browser at its normal desktop viewport. A full mobile/accessibility/cross-browser audit and Windows batch-launcher testing are outside these checks. GitHub Actions status must be read from the actual pull-request checks.

Kyle reported three hours per weekly update. Submission allocations are approximate; automated assistant execution time is separate from student practicum hours. The source and verification artifacts document technical results, not independent proof of personal time or an awarded extra-credit score.
