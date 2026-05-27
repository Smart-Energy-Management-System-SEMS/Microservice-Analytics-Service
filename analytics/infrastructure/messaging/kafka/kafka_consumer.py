import asyncio
import json
import logging
from typing import Any, Awaitable, Callable

from aiokafka import AIOKafkaConsumer

from analytics.infrastructure.messaging.kafka.events import CONSUMED_TOPICS

logger = logging.getLogger(__name__)
EventHandler = Callable[[str, dict[str, Any]], Awaitable[None]]


class KafkaConsumerAdapter:
    def __init__(self, bootstrap_servers: str, consumer_group: str, handler: EventHandler):
        self._consumer = AIOKafkaConsumer(
            *CONSUMED_TOPICS,
            bootstrap_servers=bootstrap_servers,
            group_id=consumer_group,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
            auto_offset_reset="latest",
        )
        self._handler = handler
        self._task: asyncio.Task | None = None
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        await self._consumer.start()
        self._started = True
        self._task = asyncio.create_task(self._consume())
        logger.info("Kafka consumer started")

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._started:
            await self._consumer.stop()
            self._started = False
            logger.info("Kafka consumer stopped")

    async def _consume(self) -> None:
        try:
            async for message in self._consumer:
                await self._handler(message.topic, message.value)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Kafka consumer loop stopped unexpectedly")
