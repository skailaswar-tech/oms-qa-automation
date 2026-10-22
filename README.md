# OMS API Automation

A Python test project for a mock Order Management System (OMS). The tests cover login, order creation, payment processing, and order-state validation. They also compare API responses with the records stored in SQLite.

## Technology

- Python 3.10+
- Flask for the mock OMS API
- Playwright `APIRequestContext` for HTTP requests
- pytest for fixtures and assertions
- SQLite for order and payment persistence
- GitHub Actions for CI

## Project structure

```text
oms-qa-automation/
├── .github/
│   └── workflows/
│       └── tests.yml
├── docs/
│   ├── CI_CD_Review_Notes.md
│   └── Task_1_Test_Strategy_OMS.docx
├── src/
│   ├── __init__.py
│   └── app.py
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

## Setup

Create and activate a virtual environment from the repository root.

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

Install dependencies and run the tests:

```bash
python -m pip install -r requirements.txt
python -m pytest -v
```

To run only the database checks:

```bash
python -m pytest -v tests/test_database.py
```

The tests use Playwright's API request context and do not launch a browser. The test fixture starts the Flask app locally and creates a temporary SQLite database for the test session.

## API routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/login` | Authenticate the test user |
| `POST` | `/api/orders` | Create an order |
| `POST` | `/api/orders/{id}/payment` | Simulate a payment outcome |
| `GET` | `/api/orders/{id}` | Retrieve order and payment state |

The mock app uses `qa.user@example.com` / `Passw0rd!` as test credentials. These credentials and the fixed bearer token are for local testing only and are not suitable for production authentication.

## Test coverage

- Valid login, invalid login, and order creation without authentication
- Order response fields and total amount
- Rejection of zero quantity and invalid prices
- Successful payment and order confirmation
- Failed payment and the resulting order status
- Payment requests for unknown orders and invalid payment outcomes
- Comparison of API order/payment data with SQLite records
- Rejection of a second payment for an order

The current suite contains 14 tests. Test data is isolated through a temporary database created for each pytest session.

## Database validation

The API and database tests use the same temporary SQLite database. Tests create orders through the API, query SQLite directly, and compare stored values with the API responses. Currency values are compared with Python's `Decimal` to avoid floating-point rounding issues. The schema enforces a foreign key from payments to orders and allows only one payment record per order.

## Continuous integration

The workflow in `.github/workflows/tests.yml` runs on pushes, pull requests, and manual dispatch. It installs the dependencies, runs pytest, and uploads a JUnit XML test report as the `pytest-results` artifact.

The workflow has been run in GitHub Actions, where all 14 tests passed. Subsequent runs can be checked from the repository's **Actions** tab.

## Assumptions and limitations

- The OMS is a local mock service because no existing application or API contract was provided.
- Product details are included in the order request; there is no external product catalogue.
- Payment outcomes are simulated. No payment provider or real transaction is involved.
- The project tests API behavior and database persistence; it does not automate a browser UI.
- Authentication is intentionally simplified for this test environment and is not production-ready.
