# Contributing

1. Create a branch for a concrete change, such as `fix/salary-validation`.
2. Use the documented Python 3.12 virtual environment and `requirements-dev.txt`.
3. Keep pandas analysis independent from Streamlit UI code.
4. Add a meaningful test for changed calculations or error handling.
5. Run `python -m pytest -q` with the virtual environment's Python.
6. When collecting practicum evidence, run `python scripts/verify.py` and link the resulting record.
7. Review your diff for personal data before committing. Put any private CSVs in ignored `data/private/`.
8. Describe the change, reason, and actual verification in the commit or pull request.

Do not edit generated evidence to make a failed run appear successful. Keep the failed run and record a new one after fixing the cause. Keep synthetic examples visibly labeled. Student hour logs must reflect actual participation.
