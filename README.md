# OMS QA Automation — Python, Playwright, pytest

A self-contained mock Order Management System (OMS) and API automation suite for the take-home assignment. The project covers the complete workflow:

**Login → Create Order → Simulate Payment → Validate Order and SQLite data**

## Technology

- Python 3.10+
- Flask — mock OMS REST API
- Playwright for Python (`APIRequestContext`) — API automation
- pytest — test fixtures and assertions
- SQLite — order/payment persistence and database consistency checks

## Project structure

```text
oms-qa-automation/
├── src/
│   └── app.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_order.py
│   ├── test_payment.py
│   └── test_database.py
├── docs/
│   └── Task_1_Test_Strategy_OMS.docx
├── requirements.txt
├── pytest.ini
└── README.md
```

## Setup

Python 3.10+ recommended.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

No browser binaries are required because the tests use Playwright's API request context and do not launch a browser.

## Run all tests

From the repository root:

```bash
python -m pytest -v
```

Run database checks only:

```bash
python -m pytest -v tests/test_database.py
```

The pytest session starts the local mock API on an available port and uses one temporary SQLite database shared by API requests and direct database assertions. The temporary database is removed at the end of the session.

## Mock API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/login` | Authenticate the test user |
| POST | `/api/orders` | Create and persist an order |
| POST | `/api/orders/{id}/payment` | Simulate successful or failed payment |
| GET | `/api/orders/{id}` | Retrieve persisted order and payment state |

Test-only credentials: `qa.user@example.com` / `Passw0rd!`. These credentials and the fixed bearer token are for local demonstration only, not production.

## Test coverage

- Valid login and invalid login
- Unauthorized order creation
- Order response fields, total amount, invalid quantity, and invalid price
- Successful payment and order confirmation
- Failed payment and non-confirmed order status
- Unknown order and invalid payment outcome
- API response compared with the persisted SQLite order row
- Payment amount compared with order total
- Database state checked for both successful and failed payments
- Duplicate payment request rejected; only one payment row remains

## Database consistency approach (Task 3)

The database tests use the **same temporary SQLite database used by the mock OMS API**. They create an order through the API, query SQLite directly, and compare product ID, name, quantity, unit price, total, order status, payment amount, and payment status.

Currency values are stored as decimal strings by the mock API and compared using Python `Decimal` in tests to avoid floating-point comparison issues. SQLite enforces a foreign key from payments to orders and a unique payment record per order.

## Assumptions

1. The mock OMS is the system under test because the assignment does not provide an existing application or API contract.
2. Product details are sent in the create-order request rather than fetched from an external catalogue.
3. Payment is simulated; no real payment provider or money movement is involved.
4. Successful payment results in `CONFIRMED`; failed payment results in `PAYMENT_FAILED`.
5. API tests use Playwright's `APIRequestContext`; browser UI automation is not required for this API-focused task.
6. Each pytest session uses a temporary database so tests do not depend on stale local data.
7. The fixed credentials and token are intentionally simple test fixtures, not production authentication.

## Next steps

- Task 4: add GitHub Actions CI workflow.
- Task 5: add short answers about testing non-deterministic AI outputs and challenges versus traditional testing.


## Task 4 — CI/CD with GitHub Actions

A GitHub Actions workflow is defined in `.github/workflows/tests.yml`. It runs when code is pushed, a pull request is opened or updated, or the workflow is manually triggered.

The workflow:
1. Checks out the repository.
2. Sets up Python 3.12.
3. Installs dependencies from `requirements.txt`.
4. Runs the full pytest suite and writes a JUnit XML report.
5. Uploads the test report as a workflow artifact, including when tests fail.

### Enable CI

1. Create a GitHub repository for this project.
2. Push the project files to the repository, including `.github/workflows/tests.yml`.
3. Open the repository's **Actions** tab to view the workflow run.
4. Open a workflow run to inspect logs; download the `pytest-results` artifact to review the test report.

No secrets are required because the OMS is mocked locally and the test suite does not call an external service.
