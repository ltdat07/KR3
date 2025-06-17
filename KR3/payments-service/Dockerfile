FROM python:3.10-slim

WORKDIR /app

COPY common ./common

COPY payments-service/ ./

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8002

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
