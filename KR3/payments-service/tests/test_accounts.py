import os
import uuid
import pytest
import importlib.util
from fastapi.testclient import TestClient

app_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))
spec = importlib.util.spec_from_file_location("payments_app", app_py)
payments_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(payments_app)

app = payments_app.app
client = TestClient(app)


def test_full_account_lifecycle():
    user_id = "22222222-2222-2222-2222-222222222222"
    headers = {"X-User-Id": user_id}

    # Создаём аккаунт
    resp = client.post("/accounts", json={"initial_balance": 100}, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_id"] == user_id
    assert data["balance"] == 100.0

    # Пополняем баланс
    resp = client.post("/accounts/topup", json={"amount": 50}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["balance"] == 150.0

    # Проверяем текущий баланс
    resp = client.get("/accounts/balance", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["balance"] == 150.0

    # Списываем 70 → SUCCESS и баланс 80
    order_id = str(uuid.uuid4())
    resp = client.post(
        "/accounts/charge",
        json={"order_id": order_id, "amount": 70},
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["order_id"] == order_id
    assert data["status"] == "SUCCESS"

    # Остаток
    resp = client.get("/accounts/balance", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["balance"] == pytest.approx(80.0)

    resp = client.post(
        "/accounts/charge",
        json={"order_id": str(uuid.uuid4()), "amount": 200},
        headers=headers
    )
    assert resp.status_code == 402
    assert "Insufficient funds" in resp.text
