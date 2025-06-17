````markdown
KR3: Orders & Payments Microservices

> Shopaholics’ helper 
> Система из трёх микросервисов для приёма заказов и оплаты:  
> 1. API Gateway — маршрутизатор запросов  
> 2. Orders Service — создание/просмотр заказов + transactional outbox  
> 3. Payments Service — создание/пополнение/баланс счёта + transactional inbox/outbox  

---

🚀 Быстрый старт

1. **Клонировать репозиторий**  
   ```bash
   git clone https://github.com/your-org/kr3-microservices.git
   cd kr3-microservices
````

2. **Создать файл `.env` в корне проекта**

   ```
   DATABASE_URL=postgresql+asyncpg://shop:shop_pass@postgres:5432/shopdb
   KAFKA_BOOTSTRAP_SERVERS=kafka:9092
   ORDERS_TOPIC=order_created
   PAYMENT_RESULTS_TOPIC=payment_finished
   LOG_LEVEL=DEBUG
   ```

3. **Запустить параметры**

   ```bash
   docker-compose up -d --build
   ```

4. **Проверить статус**

   ```bash
   docker-compose ps
   ```

---

## 📦 Состав сервисов

| Сервис               | Порт | Описание                                               |
| -------------------- | ---- | ------------------------------------------------------ |
| **zookeeper**        | 2181 | Kafka Zookeeper                                        |
| **kafka**            | 9092 | Kafka брокер                                           |
| **postgres**         | 5432 | PostgreSQL                                             |
| **api-gateway**      | 8000 | FastAPI: маршрутизация запросов                        |
| **orders-service**   | 8001 | FastAPI: CRUD‑заказы + transactional outbox + consumer |
| **payments-service** | 8002 | FastAPI: аккаунты + transactional inbox/outbox         |

---

## 🔧 Конфигурация окружения

Каждый сервис читает переменные окружения из `.env` (Pydantic):

* `DATABASE_URL` – URL к PostgreSQL (`postgresql+asyncpg://…`)
* `KAFKA_BOOTSTRAP_SERVERS` – адрес Kafka (`kafka:9092`)
* `ORDERS_TOPIC` – имя топика для заказов (`order_created`)
* `PAYMENT_RESULTS_TOPIC` – имя топика с результатами оплаты (`payment_finished`)
* `LOG_LEVEL` – уровень логирования (`DEBUG`, `INFO`…)
* `KAFKA_CONSUMER_GROUP` – (опционально) группа потребителей

---

## 📚 API & Swagger

После запуска доступны автоматически сгенерированные OpenAPI‑документы:

* **API Gateway**:    [http://localhost:8000/docs](http://localhost:8000/docs)
* **Orders Service**:  [http://localhost:8001/docs](http://localhost:8001/docs)
* **Payments Service**: [http://localhost:8002/docs](http://localhost:8002/docs)

В них описаны все эндпоинты, схемы запросов/ответов и примеры.

---

## 🎯 Основные эндпоинты

### API Gateway

```text
POST /accounts
POST /accounts/topup
GET  /accounts/balance
POST /accounts/charge

POST /orders
GET  /orders
GET  /orders/{order_id}
```

Все запросы требуют заголовок `X-User-Id: <UUID>`.

### Orders Service

```text
POST /orders           → создаёт заказ, откладывает событие в outbox  
GET  /orders           → список заказов пользователя  
GET  /orders/{order_id} → детали и статус заказа  
```

### Payments Service

```text
POST /accounts         → создать счёт  
POST /accounts/topup   → пополнить счёт  
GET  /accounts/balance → посмотреть баланс  
POST /accounts/charge  → списать сумму  
```

---

## ✅ Гарантии надёжности

* **Transactional Outbox** в Orders Service
* **Transactional Inbox + Outbox** в Payments Service
* **Exactly‑once** при списании средств: уникальный индекс по `payload→order_id` и отлов дубликатов
* Асинхронное межсервисное взаимодействие через Kafka

---

## 🧪 Тестирование

1. **Модульные тесты**

   ```bash
   docker-compose exec orders-service pytest --cov=.
   docker-compose exec payments-service pytest --cov=.
   ```

   Покрытие ≫ 65 %.

2. **E2E‑тесты API Gateway**

   ```bash
   docker-compose exec api-gateway pytest api-gateway/tests/test_e2e.py -q
   ```

3. **HTTP‑E2E (curl / Postman)**
   Используйте `tests/test_e2e_http.py`, или вручную:

   ```bash
   BASE=http://localhost:8000
   USER=<uuid>

   curl -X POST $BASE/accounts -H "X-User-Id:$USER" -d '{"initial_balance": 200}'
   curl -X POST $BASE/orders   -H "X-User-Id:$USER" -d '{"amount":150}'
   sleep 2
   curl -X GET  $BASE/orders/{order_id} -H "X-User-Id:$USER"
   curl -X GET  $BASE/accounts/balance -H "X-User-Id:$USER"
   ```

---

## 📂 Структура репозитория

```
.
├── api-gateway/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── tests/
│       └── test_e2e.py
├── orders-service/
│   ├── api/
│   │   └── routes.py
│   ├── migrations/
│   ├── models/
│   ├── services/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── payments-service/
│   ├── api/
│   │   └── routes.py
│   ├── migrations/
│   ├── models/
│   ├── services/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── common/              # общие утилиты, Kafka‑обёртки, DB
├── docker-compose.yml
└── .env
```
