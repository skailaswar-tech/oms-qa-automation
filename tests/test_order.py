from src.oms_api_client import OMSApiClient


def test_create_order_validates_response_details(oms_client: OMSApiClient, auth_headers):
    response = oms_client.create_order(
        auth_headers,
        product_id=101,
        product_name="Wireless Mouse",
        quantity=2,
        unit_price=19.99,
    )

    assert response.status == 201
    body = response.json()
    assert isinstance(body["order_id"], int)
    assert body["product_id"] == 101
    assert body["product_name"] == "Wireless Mouse"
    assert body["quantity"] == 2
    assert body["unit_price"] == 19.99
    assert body["total_amount"] == 39.98
    assert body["status"] == "PENDING_PAYMENT"


def test_order_rejects_zero_quantity(oms_client: OMSApiClient, auth_headers):
    response = oms_client.create_order(
        auth_headers,
        product_id=101,
        product_name="Wireless Mouse",
        quantity=0,
        unit_price=19.99,
    )

    assert response.status == 400
    assert response.json()["error"] == "quantity must be a positive integer"


def test_order_rejects_invalid_price(oms_client: OMSApiClient, auth_headers):
    response = oms_client.create_order(
        auth_headers,
        product_id=101,
        product_name="Wireless Mouse",
        quantity=1,
        unit_price=-5,
    )

    assert response.status == 400
    assert response.json()["error"] == "unit_price must be greater than zero"
