# Actual build and verification evidence

The recorded automated verification ran at **2026-11-09T18:04:37.558164-05:00 (America/New_York)**. The raw record also retains UTC timestamps. This is execution evidence from the assistant's build environment, not a student work log or practicum-hour record.

| Check | Actual result |
| --- | --- |
| Automated tests | **80 passed; 0 failed; 0 errors; 0 skipped** |
| Application/package combined statement and branch coverage | **99.3%** |
| Dependency consistency | `python -m pip check` exited successfully |
| Python / OS | 3.12.14 / Linux |
| Streamlit dashboard | AppTest runs passed, including filters, reset, and upload-processing cases |
| Real browser visual review | **Not verified**; managed preview could not access the Python executable |
| Windows installation and batch launcher | **Not run** in this Linux environment |
| GitHub publication and remote CI | **Not performed**; authenticated GitHub connection unavailable |

## Raw records

- [Console test output](verification/pytest.txt)
- [JUnit XML](verification/junit.xml)
- [Coverage JSON](verification/coverage.json)
- [Timestamps, package versions, commands, exit codes, and SHA-256 manifest](verification/verification.json)
- [Dependency check output](verification/dependency-check.txt)
- [Full installed package snapshot](environment-freeze.txt)

The verification script records hashes of application, test, script, data, requirements, and configuration files. Documentation edits made after the run do not alter those checked application inputs. The final release manifest in the ZIP identifies the packaged commit and source files.

Coverage includes `app.py` and `career_intelligence/`; it does not include launcher execution, browser rendering, GitHub, or every auxiliary-script branch. Upload integration tests substitute file bytes at the uploader boundary; actual file-picker and download delivery checks remain in the manual plan. High coverage is not proof that all defects are absent.

## Version history and integrity

The ZIP includes a real `Career-Intelligence.bundle`, a release Git-history text file, and a release manifest. Restore the bundle to inspect actual commits. The commits were created at the recorded current time with an assistant author identity, not backdated or attributed to the student. Release manifest/history files are generated after the final commit and are delivery metadata, so they are not inside the bundle's tracked source tree.

See [the development log](../docs/DEVELOPMENT_LOG.md) and [GitHub setup](../docs/GITHUB_SETUP.md). Do not substitute these automated records for your own actual dates and hours.

For a new verification run, use `python scripts/verify.py`. It creates a new timestamped folder and preserves earlier evidence.
