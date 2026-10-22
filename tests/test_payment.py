from playwright.sync_api import APIRequestContext


def create_order(api: APIRequestContext, headers) -> int:
    response = api.post(
        "/api/orders",
        headers=headers,
        data={
            "product_id": 202,
            "product_name": "USB-C Hub",
            "quantity": 1,
            "unit_price": 29.50,
        },
    )
    assert response.status == 201, response.text()
    return response.json()["order_id"]


def test_successful_payment_confirms_order(api: APIRequestContext, auth_headers):
    order_id = create_order(api, auth_headers)

    payment = api.post(
        f"/api/orders/{order_id}/payment",
        headers=auth_headers,
        data={"outcome": "success"},
    )
    assert payment.status == 200
    payment_body = payment.json()
    assert payment_body["order_id"] == order_id
    assert payment_body["payment_status"] == "SUCCESS"
    assert payment_body["order_status"] == "CONFIRMED"
    assert payment_body["amount"] == 29.5

    order = api.get(f"/api/orders/{order_id}", headers=auth_headers)
    assert order.status == 200
    assert order.json()["status"] == "CONFIRMED"
    assert order.json()["payment"]["status"] == "SUCCESS"


def test_failed_payment_does_not_confirm_order(api: APIRequestContext, auth_headers):
    order_id = create_order(api, auth_headers)

    payment = api.post(
        f"/api/orders/{order_id}/payment",
        headers=auth_headers,
        data={"outcome": "failure"},
    )
    assert payment.status == 200
    body = payment.json()
    assert body["payment_status"] == "FAILED"
    assert body["order_status"] == "PAYMENT_FAILED"

    order = api.get(f"/api/orders/{order_id}", headers=auth_headers)
    assert order.status == 200
    assert order.json()["status"] == "PAYMENT_FAILED"
    assert order.json()["payment"]["status"] == "FAILED"


def test_payment_for_unknown_order_returns_404(api: APIRequestContext, auth_headers):
    response = api.post(
        "/api/orders/999999/payment",
        headers=auth_headers,
        data={"outcome": "success"},
    )
    assert response.status == 404
    assert response.json()["error"] == "Order not found"


def test_invalid_payment_outcome_is_rejected(api: APIRequestContext, auth_headers):
    order_id = create_order(api, auth_headers)
    response = api.post(
        f"/api/orders/{order_id}/payment",
        headers=auth_headers,
        data={"outcome": "maybe"},
    )
    assert response.status == 400
    assert response.json()["error"] == "outcome must be 'success' or 'failure'"
