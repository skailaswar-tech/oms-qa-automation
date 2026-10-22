"""Small local mock Order Management System (OMS) used by the automation tests."""
from __future__ import annotations

import os
import sqlite3
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from flask import Flask, g, jsonify, request


DEFAULT_DB_PATH = os.environ.get("OMS_DB_PATH", str(Path(__file__).resolve().parent.parent / "oms.db"))
VALID_USERNAME = "qa.user@example.com"
VALID_PASSWORD = "Passw0rd!"
TEST_TOKEN = "local-test-token"


def _connect(db_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                unit_price TEXT NOT NULL,
                total_amount TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL UNIQUE,
                amount TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id)
            );
            """
        )


def _money(value: Any) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("unit_price must be a valid number")
    if not amount.is_finite() or amount <= 0:
        raise ValueError("unit_price must be greater than zero")
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def create_app(db_path: str | None = None) -> Flask:
    """Application factory. Pass a temporary DB path in tests for isolation."""
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or DEFAULT_DB_PATH
    _init_db(app.config["DB_PATH"])

    def get_db() -> sqlite3.Connection:
        if "db" not in g:
            g.db = _connect(app.config["DB_PATH"])
        return g.db

    @app.teardown_appcontext
    def close_db(_error: Exception | None = None) -> None:
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    def is_authenticated() -> bool:
        return request.headers.get("Authorization") == f"Bearer {TEST_TOKEN}"

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.post("/api/login")
    def login():
        payload = request.get_json(silent=True) or {}
        if payload.get("username") != VALID_USERNAME or payload.get("password") != VALID_PASSWORD:
            return jsonify({"error": "Invalid username or password"}), 401
        return jsonify({"access_token": TEST_TOKEN, "token_type": "Bearer"}), 200

    @app.post("/api/orders")
    def create_order():
        if not is_authenticated():
            return jsonify({"error": "Unauthorized"}), 401

        payload = request.get_json(silent=True) or {}
        product_id = payload.get("product_id")
        quantity = payload.get("quantity")
        unit_price = payload.get("unit_price")

        if isinstance(product_id, bool) or not isinstance(product_id, int) or product_id <= 0:
            return jsonify({"error": "product_id must be a positive integer"}), 400
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"error": "quantity must be a positive integer"}), 400
        try:
            price = _money(unit_price)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        product_name = str(payload.get("product_name", "")).strip()
        if not product_name:
            return jsonify({"error": "product_name is required"}), 400

        total = (price * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        connection = get_db()
        cursor = connection.execute(
            """INSERT INTO orders
               (user_id, product_id, product_name, quantity, unit_price, total_amount, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (1, product_id, product_name, quantity, str(price), str(total), "PENDING_PAYMENT"),
        )
        connection.commit()
        order_id = cursor.lastrowid
        return jsonify({
            "order_id": order_id,
            "product_id": product_id,
            "product_name": product_name,
            "quantity": quantity,
            "unit_price": float(price),
            "total_amount": float(total),
            "status": "PENDING_PAYMENT",
        }), 201

    @app.post("/api/orders/<int:order_id>/payment")
    def process_payment(order_id: int):
        if not is_authenticated():
            return jsonify({"error": "Unauthorized"}), 401

        payload = request.get_json(silent=True) or {}
        outcome = payload.get("outcome")
        if outcome not in ("success", "failure"):
            return jsonify({"error": "outcome must be 'success' or 'failure'"}), 400

        connection = get_db()
        order = connection.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if order is None:
            return jsonify({"error": "Order not found"}), 404
        if order["status"] != "PENDING_PAYMENT":
            return jsonify({"error": "Payment has already been processed for this order"}), 409

        payment_status = "SUCCESS" if outcome == "success" else "FAILED"
        order_status = "CONFIRMED" if outcome == "success" else "PAYMENT_FAILED"
        connection.execute(
            "INSERT INTO payments (order_id, amount, status) VALUES (?, ?, ?)",
            (order_id, order["total_amount"], payment_status),
        )
        connection.execute("UPDATE orders SET status = ? WHERE id = ?", (order_status, order_id))
        connection.commit()
        return jsonify({
            "order_id": order_id,
            "payment_status": payment_status,
            "order_status": order_status,
            "amount": float(Decimal(order["total_amount"])),
        }), 200

    @app.get("/api/orders/<int:order_id>")
    def get_order(order_id: int):
        if not is_authenticated():
            return jsonify({"error": "Unauthorized"}), 401
        connection = get_db()
        order = connection.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if order is None:
            return jsonify({"error": "Order not found"}), 404
        payment = connection.execute(
            "SELECT status, amount FROM payments WHERE order_id = ?", (order_id,)
        ).fetchone()
        return jsonify({
            "order_id": order["id"],
            "product_id": order["product_id"],
            "product_name": order["product_name"],
            "quantity": order["quantity"],
            "unit_price": float(Decimal(order["unit_price"])),
            "total_amount": float(Decimal(order["total_amount"])),
            "status": order["status"],
            "payment": (
                {"status": payment["status"], "amount": float(Decimal(payment["amount"]))}
                if payment else None
            ),
        }), 200

    return app
