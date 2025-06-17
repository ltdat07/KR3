import asyncio
import logging
from uuid import uuid4, UUID
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from common.messaging.consumer import KafkaConsumerWrapper
from common.messaging.producer import KafkaProducerWrapper
from models.inbox import InboxEvent
from models.outbox import OutboxEvent
from models.account import Account
from models.schema import get_sessionmaker
from config import settings

logger = logging.getLogger(__name__)

async def start_outbox_worker(
    producer: KafkaProducerWrapper,
    engine,
    settings,
):
    """
    Фоновый воркер: читает из outbox_events непроцессed события,
    отправляет их в Kafka и помечает как processed.
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
                        settings.payment_results_topic,
                        evt.payload,
                        key=None
                    )
                    evt.processed = True
                except Exception as e:
                    logger.error("Payments Outbox: failed to send %s: %s", evt.payload, e)
            await session.commit()
        await asyncio.sleep(poll_interval)

async def start_inbox_worker(
    consumer: KafkaConsumerWrapper,
    engine,
    settings,
):
    """
    Слушаем топик order_created, сохраняем событие в inbox_events,
    списываем баланс и записываем результат в outbox_events.
    """
    Session, _ = get_sessionmaker(settings.database_url)

    async def handler(msg_value: dict, msg_key: bytes):
        # Парсим
        try:
            if "order_id" in msg_value:
                order_id = msg_value["order_id"]
                user_id = UUID(msg_value["user_id"])
                amount = Decimal(str(msg_value["amount"]))
            else:
                order_id = msg_value["aggregate_id"]
                payload = msg_value["payload"]
                user_id = UUID(payload["user_id"])
                amount = Decimal(str(payload["amount"]))
        except Exception as e:
            logger.error("Payments Inbox: cannot parse message %s: %s", msg_value, e)
            return

        async with Session() as session:
            try:
                session.add(InboxEvent(
                    id=uuid4(),
                    event_type="order_created",
                    payload=msg_value
                ))
                await session.commit()
            except IntegrityError:
                await session.rollback()
                logger.info("Payments Inbox: duplicate order_id %s — skipping", order_id)
                return

        # Списываем
        status = "FAIL"
        async with Session() as session:
            account = await session.get(Account, user_id)
            if account and account.balance >= amount:
                account.balance -= amount
                status = "SUCCESS"
            # Добавляем в outbox_events
            session.add(OutboxEvent(
                id=uuid4(),
                event_type="payment_finished",
                payload={"order_id": order_id, "status": status}
            ))
            await session.commit()

        logger.info("Payments Inbox: processed %s, status=%s", order_id, status)

    # Регистрируем и стартуем
    consumer._handler = handler
    await consumer.start()
    logger.info("▶️ Payments Inbox: consumer started for topic %r", consumer._consumer.subscription())
