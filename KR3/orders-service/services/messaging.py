import asyncio
import logging
from sqlalchemy import select

from common.messaging.producer import KafkaProducerWrapper
from common.messaging.consumer import KafkaConsumerWrapper
from models.outbox import OutboxEvent
from models.order import Order, OrderStatus
from models.schema import get_sessionmaker
from config import settings

logger = logging.getLogger(__name__)

async def start_outbox_worker(
    producer: KafkaProducerWrapper,
    engine,
    settings,
):
    """
    Фоновый воркер: читает из outbox_events, отправляет в Kafka и помечает processed.
    """
    Session, _ = get_sessionmaker(settings.database_url)
    poll_interval = getattr(settings, "outbox_poll_interval", 1)

    while True:
        async with Session() as session:
            result = await session.execute(
                select(OutboxEvent).where(OutboxEvent.processed == False)
            )
            events = result.scalars().all()
            for evt in events:
                try:
                    await producer.send(
                        settings.orders_topic,
                        evt.payload,
                        key=str(evt.aggregate_id).encode("utf-8"),
                    )
                    evt.processed = True
                except Exception as e:
                    logger.error("Orders Outbox: failed to send %s: %s", evt.payload, e)
            await session.commit()
        await asyncio.sleep(poll_interval)

async def start_inbox_worker(
    consumer: KafkaConsumerWrapper,
    engine,
    settings,
):
    """
    Слушаем топик payment_finished и обновляем статус заказа.
    """
    Session, _ = get_sessionmaker(settings.database_url)

    async def handler(msg_value: dict, msg_key: bytes):
        order_id = msg_value["order_id"]
        status = msg_value["status"]

        async with Session() as session:
            order = await session.get(Order, order_id)
            if order:
                order.status = (
                    OrderStatus.FINISHED if status == "SUCCESS" else OrderStatus.CANCELLED
                )
                await session.commit()
            else:
                logger.warning("Orders Inbox: order %s not found", order_id)

    # Регистрируем и стартуем
    consumer._handler = handler
    await consumer.start()
    logger.info("▶️ Orders Inbox: consumer started for topic %r", consumer._consumer.subscription())
