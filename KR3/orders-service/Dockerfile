FROM python:3.10-slim
WORKDIR /app

COPY common ./common

COPY orders-service/ ./orders-service
WORKDIR /app/orders-service

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
