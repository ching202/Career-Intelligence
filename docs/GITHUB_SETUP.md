# Publish Career-Intelligence to GitHub

Authenticated GitHub access was not available during this build. No hosted repository, push, pull request, or GitHub Actions run is claimed. The supplied source is ready to publish as **Career-Intelligence**.

## Preserve the actual history (recommended)

The release ZIP includes `Career-Intelligence.bundle`, a portable Git bundle containing the real local commits made during this build. It preserves the recorded author and timestamps without including machine credentials or environment files.

1. Install Git if needed. Extract the ZIP and open PowerShell in the extracted folder.
2. Restore the bundle into a **new sibling folder**:

```powershell
git clone Career-Intelligence.bundle ..\Career-Intelligence-Git
cd ..\Career-Intelligence-Git
git remote remove origin
git log --oneline
```

3. On GitHub, create an empty repository named `Career-Intelligence`. Choose visibility yourself. Do not initialize it with a README, license, or gitignore because these files already exist.
4. Copy the new repository's HTTPS address. Replace the placeholder below with that exact address, then push:

```powershell
git remote add origin YOUR-ACTUAL-REPOSITORY-HTTPS-URL
git push -u origin main
```

Complete your normal GitHub authentication when Git prompts. Never place access tokens in source code, screenshots, or documentation. The Git bundle itself is a release artifact, so it does not appear inside a clone restored from that bundle.

## Publish without restoring the bundle

Use this option only if you prefer a new history. Open the extracted source folder, then run:

```powershell
git init -b main
git add .
git commit -m "Add Career Intelligence practicum project"
```

Then add the actual remote and push as above. This creates a new current-date commit; it does not recreate the original history. Configure your own name and email for your commits if Git requests them. Do not rewrite the original assistant commits as student work.

Uploading source files through GitHub's web interface is another option, but upload the extracted files, not just the ZIP. Confirm hidden configuration directories such as `.github` and `.streamlit` are present. Git upload is preferable for preserving all files and history.

## After publication

- Confirm `README.md`, `app.py`, `data/sample_jobs.csv`, and `tests/` are visible at the repository root.
- Confirm `.venv`, personal CSVs, and secrets are absent.
- Review the actual Actions result if you enable CI. Local tests work without GitHub Actions; do not enable paid usage for this project.
- Add the real repository, commit, issue, and test-run URLs to practicum reports only after they exist.
- For source-file evidence, GitHub's **Copy permalink** gives a commit-specific link.

Official reference: [Creating a new repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository).
