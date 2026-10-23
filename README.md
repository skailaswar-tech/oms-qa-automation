# OMS API Automation

A Python test project for a mock Order Management System (OMS). The tests exercise login, order creation, payment simulation, order confirmation, and consistency between API responses and SQLite records.

## Stack

- Python 3.10+
- Flask — mock OMS API
- Playwright `APIRequestContext` — API requests
- pytest — fixtures, test execution, and assertions
- SQLite — order and payment persistence
- GitHub Actions — CI test runs

## Project layout

```text
oms-qa-automation/
├── .github/workflows/tests.yml
├── docs/
│   ├── AI_Testing_Thought_Process.md
│   ├── CI_CD_Review_Notes.md
│   └── Task_1_Test_Strategy_OMS.docx
├── src/
│   ├── __init__.py
│   ├── app.py
│   └── oms_api_client.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_database.py
│   ├── test_order.py
│   └── test_payment.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Setup and run

Python 3.10 or newer is recommended. From the repository root, create and activate a virtual environment.

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies and run the suite:

```bash
python -m pip install -r requirements.txt
python -m pytest -v
```

To run only database consistency checks:

```bash
python -m pytest -v tests/test_database.py
```

The tests use Playwright's API request context and do not launch a browser, so browser binaries are not required. The test fixture starts the Flask application on a local port and uses a temporary SQLite database for the test session.

## API client and endpoints

`src/oms_api_client.py` defines `OMSApiClient`, which wraps the request context and provides reusable methods for login, order creation, payment simulation, and order retrieval. The `oms_client` fixture in `tests/conftest.py` supplies this client to the tests, keeping endpoint details separate from scenario assertions.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/login` | Authenticate the test user |
| `POST` | `/api/orders` | Create an order |
| `POST` | `/api/orders/{id}/payment` | Simulate a payment outcome |
| `GET` | `/api/orders/{id}` | Retrieve order and payment state |

The mock app uses `qa.user@example.com` / `Passw0rd!` as test credentials. They are only for this local test environment and are not production credentials.

## Test coverage

- Valid and invalid login; order creation without authentication
- Order response fields and totals; invalid quantity and price
- Successful and failed payment outcomes
- Unknown order and invalid payment outcome
- SQLite order and payment records compared with API responses
- Payment amount and status consistency
- Duplicate payment request rejected with only one payment record

## Database validation

The API and tests use the same temporary SQLite database during a test session. Tests create orders through the API, query SQLite directly, and compare stored product details, quantity, unit price, total, order status, and payment values with the API responses. Monetary values are compared using `Decimal` to avoid floating-point comparison errors. The schema also enforces a foreign key from payments to orders and one payment record per order.

## CI

The workflow at `.github/workflows/tests.yml` runs on pushes, pull requests, and manual dispatch. It installs the dependencies, runs `python -m pytest -v --junitxml=test-results.xml`, and uploads the JUnit XML report as an artifact. The current repository has a successful GitHub Actions run with all 14 tests passing.

## Assumptions and limitations

- A local mock OMS is used because no existing application or API contract was supplied.
- Product details are provided in the order request; no external product catalogue is called.
- Payment is simulated. No real payment provider or money movement is involved.
- Authentication is intentionally simplified for this test project and is not production-grade.
- The project tests API behavior and database persistence; it does not automate a browser UI.

See `docs/Task_1_Test_Strategy_OMS.docx` for the test strategy and `docs/AI_Testing_Thought_Process.md` for the short AI testing responses.
