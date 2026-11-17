# Milestone 2 · Week 7: Data ingestion and validation

**Implementation status:** the initial project supplies the components linked below. Automated results are recorded in the shared verification evidence. Personal review, work dates, hours, and submission acceptance have not been recorded.

## Objective

Build understanding and verifiable evidence for **data ingestion and validation**. This report organizes existing project artifacts and the student work still to document.

## Suggested task breakdown

- [ ] Inspect the CSV schema and regenerate the deterministic sample.
- [ ] Trace duplicate handling, missing identity fields, invalid dates, and salary exclusions.
- [ ] Create or modify a small synthetic fixture and verify the quality report.

## Prepared implementation evidence

- [Sample provenance](../../data/README.md)
- [CSV sample](../../data/sample_jobs.csv)
- [Loader](../../career_intelligence/data.py)
- [Data tests](../../tests/test_data.py)
- [Actual automated verification](../../evidence/README.md)

## Acceptance checklist

- [ ] Reproduce the bundled sample bytes with the default seed.
- [ ] Explain why missing pay does not remove a valid job.
- [ ] Demonstrate a validation error and the corresponding test.

Check these only after performing the review. An existing file is evidence of implementation, not evidence of student time.

## Personal review record

| Field | Actual value |
| --- | --- |
| Dates personally worked | |
| Actual hours | |
| Personal changes / investigations | |
| Actual GitHub commit or PR URL | |
| Local test-run directory or artifact | |
| Remaining issues | |
| Instructor feedback / acceptance | |

Use the [Week 7 update template](../weekly_updates/week_07_update.md) for the weekly submission.
