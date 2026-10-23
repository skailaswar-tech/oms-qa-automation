from src.oms_api_client import OMSApiClient


def test_login_with_valid_credentials_returns_bearer_token(oms_client: OMSApiClient):
    response = oms_client.login("qa.user@example.com", "Passw0rd!")

    assert response.status == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "Bearer"


def test_login_with_invalid_credentials_is_rejected(oms_client: OMSApiClient):
    response = oms_client.login("qa.user@example.com", "wrong-password")

    assert response.status == 401
    assert response.json()["error"] == "Invalid username or password"


def test_order_creation_without_token_is_rejected(oms_client: OMSApiClient):
    response = oms_client.create_order(
        headers=None,
        product_id=101,
        product_name="Wireless Mouse",
        quantity=2,
        unit_price=19.99,
    )

    assert response.status == 401
    assert response.json()["error"] == "Unauthorized"
