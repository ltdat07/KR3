from aiokafka import AIOKafkaConsumer
import asyncio
import json
from typing import Callable, Awaitable


class KafkaConsumerWrapper:
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        group_id: str,
        handler: Callable[[dict, bytes], Awaitable[None]] = None,
    ):

        self._consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            enable_auto_commit=False,
        )
        self._handler = handler
        self._task = None

    async def start(self):
        await self._consumer.start()
        if self._handler:
            # Запускаем фоновый task, который читает и обрабатывает
            self._task = asyncio.create_task(self._consume_loop())

    async def stop(self):
        if self._task:
            self._task.cancel()
        await self._consumer.stop()

    async def _consume_loop(self):
        try:
            async for msg in self._consumer:
                await self._handler(msg.value, msg.key)
                await self._consumer.commit()
        except asyncio.CancelledError:
            pass
