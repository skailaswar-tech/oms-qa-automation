# CI/CD Review Notes

- **Workflow:** `.github/workflows/tests.yml`
- **Triggers:** push, pull request, and manual workflow dispatch
- **Runner:** GitHub-hosted Ubuntu
- **Python version:** 3.12
- **Test command:** `python -m pytest -v --junitxml=test-results.xml`
- **Artifact:** `pytest-results` (JUnit XML report)
- **External credentials:** not required; the OMS runs locally as a mock service

The workflow checks out the repository, installs the dependencies, runs the pytest suite, and uploads the test report. The workflow was verified in GitHub Actions, with all 14 tests passing in the successful run. The report is available as an artifact on that workflow run.
