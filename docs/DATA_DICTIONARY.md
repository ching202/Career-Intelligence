# CSV data dictionary

The input must be UTF-8 CSV (a UTF-8 BOM is accepted), with a comma delimiter and one record per job ID. All 13 columns below are required, although several cell values may be blank. Extra columns are ignored. Header whitespace/case is normalized; duplicate header names are rejected. Quote values containing commas, such as `"Seattle, WA"`.

| Column | Example | Rules |
| --- | --- | --- |
| `job_id` | `JOB-001` | Nonempty, unique; compared case-sensitively after trimming. |
| `title` | `Backend Developer` | Nonempty. |
| `company` | `Example Studio` | Blank becomes `Unknown`. |
| `location` | `Seattle, WA` | Nonempty; supplied labels are not geocoded or merged. |
| `work_mode` | `Remote` | `Remote`, `Hybrid`, `On-site`, `Unknown`; common onsite aliases accepted. Unrecognized values become `Unknown`. |
| `experience_level` | `Entry` | `Internship`, `Entry`, `Mid`, `Senior`, `Lead`, `Unknown`; junior/entry-level/mid-level aliases accepted. |
| `salary_min` | `80000` | Plain positive numeric lower bound, or blank. No `$`, comma separators, or `80k`. |
| `salary_max` | `100000` | Plain numeric upper bound ≥ lower bound, or blank. A fixed salary uses the same value for both bounds. |
| `salary_currency` | `USD` | Case-insensitive; only USD contributes to salary comparisons. |
| `salary_period` | `annual` | `annual`, `monthly`, `weekly`, `hourly`; yearly/year/month/week/hour aliases accepted. |
| `skills` | `Python;SQL;Docker` | Explicit tokens separated by semicolon, pipe, or comma. Semicolon recommended. Blank allowed. |
| `posted_date` | `2026-10-01` | Strict `YYYY-MM-DD` calendar day; blank/invalid dates are retained as undated. |
| `data_source` | `Synthetic sample; not real vacancies` | Provenance label carried into exports; blank becomes `Unspecified`. |

Use the dashboard's **Download CSV template** for a header-only file. It must contain at least one job before upload. The loader rejects files over 10 MiB, more than 50,000 records, binary/null characters, malformed quoting, and inconsistent record widths.

## Derived fields

| Field | Meaning |
| --- | --- |
| `source_row` | Logical CSV record number including the header (multiline fields are one record). |
| `skill_tokens` | Deduplicated normalized tokens used internally. |
| `annual_min_usd` / `annual_max_usd` | Comparable annualized USD range bounds, or missing. |
| `salary_mid_usd` | Midpoint of a comparable annualized USD range, or missing. |
| `salary_status` | Included (USD), Missing salary, Invalid salary, Unsupported currency, or Unknown pay period. |

Rows missing `job_id`, `title`, or `location` are dropped. Duplicate IDs keep the first remaining row; later rows are dropped even if they have more complete salary data. This deterministic policy avoids double counting but does not identify duplicate postings with different IDs.

All retained rows are included in job counts. Missing/invalid pay, unsupported currencies, and unknown pay periods are excluded only from salary calculations. When several salary issues overlap, one primary salary status is reported, with missing pay taking precedence, then unsupported currency, then unknown period, then invalid numbers.

Recognized language tokens: Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, R, Scala, SQL, Dart, Bash. SQL is a query language included for practical job-data analysis. Frameworks/platforms appear only in the **All skill tokens** view. Unknown tokens are retained, not guessed.

Exports preserve provenance and add computed salary columns. For spreadsheet safety, text beginning with formula/control prefixes is escaped with a leading apostrophe. Blank dates remain blank. Reimporting exported files recalculates derived values from the original salary bounds; invalid input rows previously dropped cannot be recovered from an export.
