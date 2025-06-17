FROM python:3.10-slim

WORKDIR /app

# 1) Общий пакет (берём из ./common в корне)
COPY common ./common

# 2) Код самого payments-service
COPY payments-service/ ./

# 3) Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Чтобы PYTHONPATH знал, где искать common
ENV PYTHONPATH=/app

EXPOSE 8002

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
