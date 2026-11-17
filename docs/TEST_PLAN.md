# Test plan and acceptance checks

The automated suite checks observable behavior and independently calculated examples. It uses synthetic fixtures with small, known expected values. Run it with the virtual environment's Python, not an unrelated system interpreter.

```bash
python -m pytest -q
python scripts/verify.py
```

`verify.py` refuses to overwrite an existing output directory. Its default output is an ignored `evidence/local-runs/<actual-UTC-timestamp>/` folder. Copy only the evidence you intend to submit into a tracked folder; never modify its recorded results.

## Automated coverage

| Area | Examples | Evidence |
| --- | --- | --- |
| File validation | UTF-8/BOM, headers, malformed CSV, file/row limits | [test_data.py](../tests/test_data.py) |
| Cleaning | Missing identity, duplicate IDs, unknown categories, bad dates | [test_data.py](../tests/test_data.py) |
| Salary mathematics | Annual/hourly/weekly/monthly, zero/negative/reversed/nonfinite ranges, non-USD | [test_data.py](../tests/test_data.py), [test_analytics.py](../tests/test_analytics.py) |
| Skills | Alias normalization, deduplication, exact Java/JavaScript and C-family handling | [test_data.py](../tests/test_data.py), [test_analytics.py](../tests/test_analytics.py) |
| Filters | Any/all skills, literal text, categories, inclusive dates and salary, missing-value choices | [test_analytics.py](../tests/test_analytics.py) |
| Aggregation | Known median/count/coverage, locations, missing weeks, empty frames | [test_analytics.py](../tests/test_analytics.py) |
| Export | Valid CSV, provenance, empty exports, formula-prefix escaping | [test_analytics.py](../tests/test_analytics.py) |
| App interactions | Startup, sample notice, filtering, reset, upload mode and processing, invalid/empty/no-salary views | [test_app.py](../tests/test_app.py) |
| Reproduction | Generator reproduces sample bytes | [test_sample_generator.py](../tests/test_sample_generator.py) |

Upload AppTest cases mock only the file-uploader return value, then execute the actual parsing, analytics, and rendering code. They do not operate an operating-system file picker. AppTest also does not verify Plotly pixels, download delivery through a real browser, layout on iPhone, or Windows batch execution.

## Manual checks on the student's computer

Leave these unchecked until actually performed. Add real dates and screenshots if permitted.

| Done | Check | Expected behavior | Actual result / evidence |
| --- | --- | --- | --- |
| [ ] | Fresh Python 3.12 installation and setup | Dependencies install; app starts | |
| [ ] | Launch `START_WINDOWS.bat` | Local browser opens; no traceback | |
| [ ] | Open each of the five tabs | Charts/tables are readable with no clipping | |
| [ ] | Narrow the browser window | Controls and tables remain usable | |
| [ ] | Filter Remote + Python | Count decreases; remote share becomes 100% | |
| [ ] | Search for a nonexistent title; reset | Empty message appears; reset restores 300 sample rows | |
| [ ] | Upload the bundled sample with the actual picker | Sample notice remains; charts populate | |
| [ ] | Upload a malformed or unrelated CSV | Useful error appears; application stays usable | |
| [ ] | Download filtered records, demand, and quality CSVs | Download opens with expected rows and provenance | |
| [ ] | Restart without internet after setup | Bundled dashboard works offline | |
| [ ] | Run verification locally | Real local test evidence is created | |

## Actual verification status

See [evidence/README.md](../evidence/README.md) and the raw files under [evidence/verification/](../evidence/verification/). Coverage measures the application and `career_intelligence` package; it does not establish correctness of all possible inputs or cover launcher/platform behavior.

The included GitHub Actions workflow targets Python 3.11, 3.12, and 3.13 on Ubuntu. Those remote matrix jobs are configuration, not evidence of completed runs. The recorded build checks were performed on Python 3.12 in Linux.
