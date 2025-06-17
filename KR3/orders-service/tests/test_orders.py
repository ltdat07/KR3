import uuid
import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_create_and_get_order():
    # Используем фиксированный user_id
    user_id = "11111111-1111-1111-1111-111111111111"
    headers = {"X-User-Id": user_id}

    # Создаём заказ
    resp = client.post("/orders", json={"amount": 123.45}, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["amount"] == 123.45
    assert data["user_id"] == user_id
    order_id = data["id"]

    # Получаем список заказов
    resp2 = client.get("/orders", headers=headers)
    assert resp2.status_code == 200
    orders = resp2.json()
    assert any(o["id"] == order_id for o in orders)

    # Получаем заказ по ID
    resp3 = client.get(f"/orders/{order_id}", headers=headers)
    assert resp3.status_code == 200
    order = resp3.json()
    assert order["id"] == order_id
    assert order["amount"] == 123.45
    assert order["status"] == "NEW"
