# Requirements and evidence

| Requested outcome | Implementation | Verification / status |
| --- | --- | --- |
| Free Python, pandas, Streamlit | [Requirements](../requirements.txt), [app](../app.py) | Dependency check and AppTest passed; no API keys required |
| Public CSV or labeled sample | [300-row sample](../data/sample_jobs.csv), [provenance](../data/README.md) | Exact deterministic reproduction test; visible sample notice |
| Salary analysis | [Analysis module](../career_intelligence/analytics.py), Salaries tab | Known-value annualization/median/exclusion tests |
| Language demand | Exact normalized tokens and mention shares | Alias, distinct-token, duplicate, and denominator tests |
| Location analysis | Location counts, salary sample sizes, filter | Known grouped-count and filtering tests |
| Interactive dashboard | Five tabs and shared sidebar filters | AppTest startup, filter, reset, empty-state, and upload processing tests |
| Automated tests run | [Tests](../tests/) | [Actual results](../evidence/README.md) |
| Professional installation guide | [README](../README.md), [user guide](USER_GUIDE.md) | Linux environment used successfully; Windows commands/launcher need target-PC check |
| GitHub-ready repository | Git history, .gitignore, CI workflow, MIT License | Local Git repository and release bundle; remote publication pending access |
| Six milestones: Weeks 6–11 | [Milestone index](MILESTONES.md) | Six reports with source evidence and personal acceptance fields |
| Six weekly updates | [Weekly templates](weekly_updates/README.md) | Six templates with task/time/evidence/reflection fields left unfilled |
| Honest development evidence | [Build log](DEVELOPMENT_LOG.md), [raw evidence](../evidence/README.md) | Actual execution times, results, hashes, and real local commits; no fabricated hours |

The sample supports a software demonstration. Using real market conclusions in an academic report requires a separately sourced, appropriately licensed and documented dataset.
