"""Reusable client for the mock OMS API used by the automated tests."""
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse


class OMSApiClient:
    """Encapsulate OMS endpoints so tests focus on behavior and assertions."""

    def __init__(self, request: APIRequestContext):
        self._request = request

    def health(self) -> APIResponse:
        return self._request.get("/health")

    def login(self, username: str, password: str) -> APIResponse:
        return self._request.post(
            "/api/login",
            data={"username": username, "password": password},
        )

    def create_order(
        self,
        headers: dict[str, str] | None,
        *,
        product_id: int,
        product_name: str,
        quantity: int,
        unit_price: float,
    ) -> APIResponse:
        payload: dict[str, Any] = {
            "product_id": product_id,
            "product_name": product_name,
            "quantity": quantity,
            "unit_price": unit_price,
        }
        return self._request.post("/api/orders", headers=headers or {}, data=payload)

    def simulate_payment(
        self, order_id: int, headers: dict[str, str] | None, outcome: str
    ) -> APIResponse:
        return self._request.post(
            f"/api/orders/{order_id}/payment",
            headers=headers or {},
            data={"outcome": outcome},
        )

    def get_order(
        self, order_id: int, headers: dict[str, str] | None
    ) -> APIResponse:
        return self._request.get(f"/api/orders/{order_id}", headers=headers or {})
