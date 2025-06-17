# KR3/api-gateway/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 1) Общий пакет
COPY common ./common

# 2) Весь код API‑Gateway (app.py, requirements.txt, прочие модули)
COPY api-gateway/ ./

# 3) Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 4) Экспоним порт
EXPOSE 8000

# 5) Запуск Uvicorn (app.py должен оказаться в /app/app.py)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
