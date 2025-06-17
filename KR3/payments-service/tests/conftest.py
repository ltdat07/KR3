# payments-service/tests/conftest.py
import os

# Перед запуском приложения под pytest выставляем флаг
os.environ["TESTING"] = "1"
