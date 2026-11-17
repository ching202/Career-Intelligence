# Release and handoff

The delivered package contains a working implementation, synthetic sample, automated tests, source documentation, six milestone reports, six blank weekly templates, and actual build evidence. The initial build is not a claim that the student completed six weeks of work.

## Releasing a future version

1. Implement the change on a real Git branch and review the diff.
2. Run the appropriate tests. For final evidence, use `python scripts/verify.py`.
3. Perform any relevant manual checks in [TEST_PLAN.md](TEST_PLAN.md).
4. Update documentation and identify known limitations honestly.
5. Commit the actual change with the current timestamp.
6. If preserving history in a ZIP, run `git bundle create Career-Intelligence.bundle --all` from a clean repository. Do not include secrets in Git in the first place.
7. Run `python scripts/package_project.py` to create the ZIP in the parent directory.
8. Inspect the archive and confirm it includes the source, sample, tests, documentation, and intended evidence; omit environments and private data.

## Student handoff checklist

- [ ] Download and extract the complete package on the home PC.
- [ ] Follow the README and run the app locally.
- [ ] Complete the relevant manual checks and record actual results.
- [ ] Restore the bundle or initialize Git, then publish when access permits.
- [ ] Add actual GitHub links to practicum updates.
- [ ] Review, understand, and adapt the implementation.
- [ ] Log only actual personal work dates and hours.
- [ ] Rehearse the instructor demonstration.

No paid hosting or API access is required. Public hosting is optional future work and has not been configured.
