from aiokafka import AIOKafkaProducer
import asyncio
import json


class KafkaProducerWrapper:
    def __init__(self, bootstrap_servers: str):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    async def start(self):
        await self._producer.start()

    async def stop(self):
        await self._producer.stop()

    async def send(self, topic: str, value: dict, key: bytes = None):
        await self._producer.send_and_wait(topic, value=value, key=key)