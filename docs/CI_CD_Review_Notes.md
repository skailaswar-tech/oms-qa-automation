# CI/CD Review Notes

- Workflow: `.github/workflows/tests.yml`
- Triggers: push, pull request, and manual workflow dispatch
- Runner: GitHub-hosted Ubuntu
- Python: 3.12
- Test command: `python -m pytest -v --junitxml=test-results.xml`
- Artifact: `pytest-results` (JUnit XML report)
- External API credentials: not required; the OMS is mocked locally

The workflow has been run in the GitHub repository. The latest verified run completed successfully and reported **14 passed**. The JUnit XML test report was uploaded as a workflow artifact.
