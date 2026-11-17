# Week 7: data ingestion and validation

Technical work and publication date: **November 17, 2026**. This evidence supports a late Week 7 submission; commits and verification records are not backdated to the November 15 due date.

## Changes and observed results

1. Added a seven-record synthetic fixture covering a duplicate identifier, missing salary, invalid date, missing title, non-USD currency, and a reversed salary range. The loader retains five jobs, drops two unusable/duplicate records, and reports six issues against their original CSV record numbers.
2. Added three regression tests: exact cleaning/audit outcomes, cleaned CSV export/reimport consistency, and an actionable error for a missing required `skills` header. Two jobs have usable USD pay; salary coverage is 40%, and their median annual midpoint is $100,000. These are synthetic test expectations, not job-market findings.
3. Added `.gitattributes` to keep source and sample CSV line endings at LF and Windows batch files at CRLF. Windows `core.autocrlf=true` had changed the checked-out sample bytes, causing a mismatch with the deterministic generator despite equivalent CSV content. The normalization restores reproducible bytes.

## Evidence

- [Synthetic fixture](../tests/fixtures/validation_cases.csv)
- [Three regression tests](../tests/test_validation_fixture.py)
- [Sample generator reproduction test](../tests/test_sample_generator.py)
- [Line-ending configuration](../.gitattributes)
- [Before-fix byte comparison](../evidence/week7-before.json)
- [Cleaned fixture export](../evidence/week7-data/cleaned_jobs.csv)
- [Quality audit](../evidence/week7-data/quality_issues.csv)
- [Fixture summary](../evidence/week7-data/summary.json)
- [Initial Windows run](../evidence/week7-verification/verification.json)
- [Publication verification console output](../evidence/week7-publication-verification/pytest.txt)
- [Publication verification metadata and source hashes](../evidence/week7-publication-verification/verification.json)

The initial Windows run completed with **83 tests passed, zero failures/errors/skips, and 99.3% statement/branch coverage**. The publication run verifies the final normalized source. Both use Python 3.12.14 with the pinned project requirements; the raw files preserve actual commands, timestamps, exit codes, and package versions. `pip check` also passes.

Streamlit checks use AppTest. A real browser, physical upload/download controls, and the Windows batch launcher have not been manually verified. Local results do not establish remote GitHub Actions status; inspect the actual PR checks for that result.

## Contribution and reporting

Kyle directed the project and requested publication in response to instructor feedback. OpenAI Codex assisted with code, tests, command execution, and documentation. Kyle reported three hours per weekly update; approximate task allocations in the submission are not instrumented time records. Automated runtime is not counted as student practicum time.
