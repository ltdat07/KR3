import os
import pytest
import uuid
import time
import importlib.util
from fastapi.testclient import TestClient

os.environ["ORDERS_URL"] = "http://127.0.0.1:8001"
os.environ["PAYMENTS_URL"] = "http://127.0.0.1:8002"

gw_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "app.py")
)
spec = importlib.util.spec_from_file_location("gw_app", gw_path)
gw_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gw_app)
app = gw_app.app
client = TestClient(app)


@pytest.fixture
def user_id():
    return str(uuid.uuid4())


def test_e2e_order_payment_flow(user_id):
    headers = {"X-User-Id": user_id}

    # Создаём аккаунт
    r = client.post("/accounts", json={"initial_balance": 200}, headers=headers)
    assert r.status_code == 201, r.text

    # Создаём заказ
    r = client.post("/orders", json={"amount": 150}, headers=headers)
    assert r.status_code == 201, r.text
    order = r.json()
    order_id = order["id"]

    # Даём сервисам время на обмен сообщениями через Kafka
    time.sleep(2)

    # Проверяем, что статус заказа FINISHED
    r = client.get(f"/orders/{order_id}", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "FINISHED"

    # Проверяем остаток
    r = client.get("/accounts/balance", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["balance"] == pytest.approx(50.0)
