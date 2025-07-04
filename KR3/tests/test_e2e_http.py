import os, time, uuid, pytest, requests

BASE = os.getenv("GATEWAY_BASE", "http://127.0.0.1:8000")

@pytest.fixture
def user_id():
    return str(uuid.uuid4())

def test_e2e_order_payment_flow(user_id):
    headers = {"X-User-Id": user_id}

    # Создаём аккаунт
    r = requests.post(f"{BASE}/accounts", json={"initial_balance": 200}, headers=headers)
    assert r.status_code == 201, r.text

    # Создаём заказ
    r = requests.post(f"{BASE}/orders", json={"amount": 150}, headers=headers)
    assert r.status_code == 201, r.text
    order_id = r.json()["id"]

    # Ждём обработки
    time.sleep(2)

    r = requests.get(f"{BASE}/orders/{order_id}", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "FINISHED"

    r = requests.get(f"{BASE}/accounts/balance", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["balance"] == pytest.approx(50.0)
