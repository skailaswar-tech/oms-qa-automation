# Task 4 — CI/CD Review Notes

- Workflow: `.github/workflows/tests.yml`
- Trigger events: push, pull request, manual workflow dispatch
- Runner: GitHub-hosted Ubuntu
- Python: 3.12
- Test command: `python -m pytest -v --junitxml=test-results.xml`
- Artifact: `pytest-results` (JUnit XML report)
- External API credentials: not required for the mock OMS project

The workflow file is added to the project. A real GitHub Actions run can only be confirmed after this project is pushed to a GitHub repository and the workflow executes there.
