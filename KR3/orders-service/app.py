import asyncio
import logging
import os
import sys

from fastapi import FastAPI, APIRouter
from sqlalchemy import text

from common.utils.db import create_db_engine, init_db
from config import settings  # <-- обязательно

# Признак, что мы под pytest
TESTING = os.getenv("TESTING", "").lower() in ("1", "true", "yes")

app = FastAPI(title="Orders Service", version="0.1.0")

# Подключаем маршруты CRUD для заказов
from api.routes import router as orders_router
app.include_router(orders_router, prefix="/orders", tags=["orders"])

# Отладочный endpoint
debug = APIRouter()
@debug.get("/tables")
async def tables():
    engine = app.state.db_engine
    async with engine.connect() as conn:
        res = await conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname='public';"
        ))
        return {"tables": [r[0] for r in res]}
app.include_router(debug, prefix="/debug", tags=["debug"])

if not TESTING:
    from common.messaging.producer import KafkaProducerWrapper
    from common.messaging.consumer import KafkaConsumerWrapper
    from services.messaging import start_inbox_worker, start_outbox_worker

    logger = logging.getLogger(__name__)

    @app.on_event("startup")
    async def on_startup():
        # 1) Инициализация БД и миграции
        import models.order, models.outbox  # noqa
        engine = create_db_engine(settings.database_url)
        for _ in range(10):
            try:
                await init_db(engine)
                logger.info("DB initialized")
                break
            except Exception as e:
                logger.warning(f"DB init failed: {e}; retrying…")
                await asyncio.sleep(1)
        app.state.db_engine = engine

        # 2) Producer
        prod = KafkaProducerWrapper(settings.kafka_bootstrap_servers)
        await prod.start()
        app.state.kafka_producer = prod

        # 3) Consumer
        consumer = KafkaConsumerWrapper(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            topic=settings.payment_results_topic,
            group_id=settings.kafka_consumer_group
        )
        app.state.kafka_consumer = consumer

        # 4) Запуск воркеров
        app.state.outbox_task = asyncio.create_task(
            start_outbox_worker(app.state.kafka_producer, engine, settings)
        )
        app.state.inbox_task = asyncio.create_task(
            start_inbox_worker(app.state.kafka_consumer, engine, settings)
        )

    @app.on_event("shutdown")
    async def on_shutdown():
        app.state.inbox_task.cancel()
        app.state.outbox_task.cancel()
        await app.state.kafka_producer.stop()
        await app.state.kafka_consumer.stop()
        await app.state.db_engine.dispose()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8001, log_level="info")
