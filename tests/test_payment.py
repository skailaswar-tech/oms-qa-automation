from src.oms_api_client import OMSApiClient


def create_order(oms_client: OMSApiClient, headers, quantity=1, unit_price=29.50) -> int:
    response = oms_client.create_order(
        headers,
        product_id=202,
        product_name="USB-C Hub",
        quantity=quantity,
        unit_price=unit_price,
    )
    assert response.status == 201, response.text()
    return response.json()["order_id"]


def test_successful_payment_confirms_order(oms_client: OMSApiClient, auth_headers):
    order_id = create_order(oms_client, auth_headers)

    payment = oms_client.simulate_payment(order_id, auth_headers, outcome="success")
    assert payment.status == 200
    payment_body = payment.json()
    assert payment_body["order_id"] == order_id
    assert payment_body["payment_status"] == "SUCCESS"
    assert payment_body["order_status"] == "CONFIRMED"
    assert payment_body["amount"] == 29.5

    order = oms_client.get_order(order_id, auth_headers)
    assert order.status == 200
    assert order.json()["status"] == "CONFIRMED"
    assert order.json()["payment"]["status"] == "SUCCESS"


def test_failed_payment_does_not_confirm_order(oms_client: OMSApiClient, auth_headers):
    order_id = create_order(oms_client, auth_headers)

    payment = oms_client.simulate_payment(order_id, auth_headers, outcome="failure")
    assert payment.status == 200
    body = payment.json()
    assert body["payment_status"] == "FAILED"
    assert body["order_status"] == "PAYMENT_FAILED"

    order = oms_client.get_order(order_id, auth_headers)
    assert order.status == 200
    assert order.json()["status"] == "PAYMENT_FAILED"
    assert order.json()["payment"]["status"] == "FAILED"


def test_payment_for_unknown_order_returns_404(oms_client: OMSApiClient, auth_headers):
    response = oms_client.simulate_payment(999999, auth_headers, outcome="success")
    assert response.status == 404
    assert response.json()["error"] == "Order not found"


def test_invalid_payment_outcome_is_rejected(oms_client: OMSApiClient, auth_headers):
    order_id = create_order(oms_client, auth_headers)
    response = oms_client.simulate_payment(order_id, auth_headers, outcome="maybe")
    assert response.status == 400
    assert response.json()["error"] == "outcome must be 'success' or 'failure'"
