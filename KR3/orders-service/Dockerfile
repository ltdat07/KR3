FROM python:3.10-slim
WORKDIR /app

# 1) Копируем общий пакет
COPY common ./common

# 2) Копируем код сервиса
COPY orders-service/ ./orders-service
WORKDIR /app/orders-service

# 3) Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Чтобы Python видел пакет common
ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
