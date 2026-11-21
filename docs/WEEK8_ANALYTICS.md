# Week 8: salary, language, and location analytics

Technical work date: **November 20, 2026**. Prepared with OpenAI Codex assistance for Career Intelligence. All examples below are fictional test records, not real salary or labor-market findings.

## User-visible improvement

Group tables previously showed a median and usable-salary count, but did not show the percentage of jobs represented by that median. The experience-level and location tables now display **Salary coverage (%)**, and location downloads include the numeric `salary_coverage` field. All three supported grouping functions use the same definition.

Coverage uses only the current group's filtered jobs as its denominator. A location with three jobs and two usable USD pay ranges has 66.7% coverage. Its third job still counts even when its pay cannot be compared. A group with no usable salaries shows 0% coverage and no median. An empty result retains the expected export columns.

## Worked salary calculations

[Seven-record fixture](../tests/fixtures/analytics_cases.csv) and [recorded annualized values](../evidence/week8-analytics/annualized_salaries.csv).

| Job | Given range | Midpoint calculation | Annual USD midpoint |
| --- | --- | --- | ---: |
| ANNUAL | $80,000–$100,000/year | (80,000 + 100,000) / 2 | $90,000 |
| MONTHLY | $8,000–$10,000/month | 9,000 × 12 | $108,000 |
| HOURLY | $50–$60/hour | 55 × 2,080 | $114,400 |
| WEEKLY | $1,500–$2,000/week | 1,750 × 52 | $91,000 |
| NO-SKILLS | $90,000–$110,000/year | (90,000 + 110,000) / 2 | $100,000 |
| MISSING | No stated range | Retained in job counts; excluded from pay statistics | N/A |
| CAD | CAD 70,000–90,000/year | No currency conversion; excluded from USD statistics | N/A |

Sorted usable midpoints are $90,000, $91,000, **$100,000**, $108,000, and $114,400. The median is **$100,000**. Overall salary coverage is **5 / 7 × 100 = 71.43%**. The hourly calculation assumes 40 hours/week for 52 weeks and does not establish actual earnings.

## Exact skills and denominators

The repeated `Java` token on ANNUAL counts once. Java and JavaScript remain distinct, as do C, C++, and C#. SQL appears on two jobs, JavaScript on three, Python on three, and Java/C/C++/C# on one job each. The job without skills remains in the seven-job denominator.

Thus Java's share is **1 / 7 = 14.29%**, and JavaScript's share is **3 / 7 = 42.86%**. Combined skill shares are **12 / 7 = 171.43%**, which is valid because each job can mention multiple skills. [Recorded language results](../evidence/week8-analytics/languages.csv).

## Locations and filtering

| Location | Jobs | Usable USD ranges | Median annual midpoint | Salary coverage |
| --- | ---: | ---: | ---: | ---: |
| Seattle, WA | 3 | 2 | $99,000 | 66.67% |
| Portland, OR | 2 | 2 | $102,700 | 100.00% |
| Toronto, ON | 2 | 1 | $100,000 | 50.00% |

Filtering to **Seattle + Remote** retains ANNUAL and MISSING. The filtered view has two jobs, one usable pay range, a $90,000 median, and **50% salary coverage**. Its Java, Python, and SQL shares are each 50%. This confirms that metrics use the filtered denominator rather than the original seven jobs.

[All locations](../evidence/week8-analytics/locations.csv) · [Seattle + Remote](../evidence/week8-analytics/seattle_remote_locations.csv) · [Experience groups](../evidence/week8-analytics/experience_levels.csv) · [Work arrangements](../evidence/week8-analytics/work_modes.csv).

## Verification and reproduction

[Regression tests](../tests/test_analytics_milestone.py) cover the four pay periods, overall median, exact language tokens, all grouping modes, filtered denominators, missing pay, empty results, CSV exports, and the Streamlit table behavior after an uploaded fixture is filtered.

Run `python -m pytest -q` with the pinned project requirements. Run `python scripts/record_analytics_example.py --output evidence/local-runs/week8-example` to generate a fresh copy of the examples. The output directory must not already exist. `python scripts/verify.py` records a fresh full-suite check without overwriting earlier evidence.

The full Windows run passed **100 tests** with **zero failures/errors/skips** and **99.4% combined statement/branch coverage**. The dependency consistency check passed. This includes 17 new regression cases beyond the 83-test Week 7 baseline.

The full run is recorded under [evidence/week8-verification](../evidence/week8-verification), including console output, coverage, JUnit results, timestamps, and source hashes. Streamlit verification uses AppTest; the physical browser file picker, rendering, and Windows batch launcher are not claimed as manually tested.

Kyle reported three hours per weekly update. The submission's task allocations are approximate, and automated assistant runtime is not counted as student practicum hours. GitHub links document the actual code and results, not independent proof of personal time.
