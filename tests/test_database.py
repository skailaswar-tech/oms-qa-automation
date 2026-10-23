"""Verify the mock OMS API state against its actual SQLite database."""
import sqlite3
from decimal import Decimal

from src.oms_api_client import OMSApiClient


def create_order(oms_client: OMSApiClient, headers, quantity=2, unit_price=19.99) -> dict:
    response = oms_client.create_order(
        headers,
        product_id=101,
        product_name="Wireless Mouse",
        quantity=quantity,
        unit_price=unit_price,
    )
    assert response.status == 201, response.text()
    return response.json()


def fetch_rows(db_path, order_id):
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        order = connection.execute(
            """SELECT id, product_id, product_name, quantity, unit_price,
                      total_amount, status
               FROM orders WHERE id = ?""",
            (order_id,),
        ).fetchone()
        payment = connection.execute(
            "SELECT order_id, amount, status FROM payments WHERE order_id = ?",
            (order_id,),
        ).fetchone()
    return (dict(order) if order else None, dict(payment) if payment else None)


def test_created_order_is_persisted_consistently(oms_client, auth_headers, oms_db_path):
    created = create_order(oms_client, auth_headers)
    stored_order, stored_payment = fetch_rows(oms_db_path, created["order_id"])

    assert stored_order is not None
    assert stored_order["id"] == created["order_id"]
    assert stored_order["product_id"] == created["product_id"]
    assert stored_order["product_name"] == created["product_name"]
    assert stored_order["quantity"] == created["quantity"]
    assert Decimal(stored_order["unit_price"]) == Decimal("19.99")
    assert Decimal(stored_order["total_amount"]) == Decimal("39.98")
    assert stored_order["status"] == "PENDING_PAYMENT"
    assert stored_payment is None


def test_successful_payment_matches_db_and_confirms_order(oms_client, auth_headers, oms_db_path):
    created = create_order(oms_client, auth_headers, quantity=2, unit_price=19.99)
    order_id = created["order_id"]

    payment = oms_client.simulate_payment(order_id, auth_headers, outcome="success")
    assert payment.status == 200
    response_payment = payment.json()
    stored_order, stored_payment = fetch_rows(oms_db_path, order_id)

    assert stored_order["status"] == response_payment["order_status"] == "CONFIRMED"
    assert stored_payment is not None
    assert stored_payment["order_id"] == order_id
    assert stored_payment["status"] == response_payment["payment_status"] == "SUCCESS"
    assert Decimal(stored_payment["amount"]) == Decimal(stored_order["total_amount"])
    assert Decimal(stored_payment["amount"]) == Decimal("39.98")


def test_failed_payment_state_matches_db(oms_client, auth_headers, oms_db_path):
    created = create_order(oms_client, auth_headers, quantity=1, unit_price=29.50)
    order_id = created["order_id"]

    payment = oms_client.simulate_payment(order_id, auth_headers, outcome="failure")
    assert payment.status == 200
    stored_order, stored_payment = fetch_rows(oms_db_path, order_id)

    assert stored_order["status"] == "PAYMENT_FAILED"
    assert stored_payment["status"] == "FAILED"
    assert Decimal(stored_payment["amount"]) == Decimal(stored_order["total_amount"])
    assert stored_order["status"] != "CONFIRMED"


def test_db_enforces_one_payment_per_order(oms_client, auth_headers, oms_db_path):
    created = create_order(oms_client, auth_headers, quantity=1, unit_price=10.00)
    order_id = created["order_id"]
    payment = oms_client.simulate_payment(order_id, auth_headers, outcome="success")
    assert payment.status == 200

    # A second payment request must be rejected and must not create another row.
    second = oms_client.simulate_payment(order_id, auth_headers, outcome="success")
    assert second.status == 409
    with sqlite3.connect(oms_db_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM payments WHERE order_id = ?", (order_id,)
        ).fetchone()[0]
    assert count == 1
