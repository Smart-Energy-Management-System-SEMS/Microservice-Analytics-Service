import asyncio
import json
import logging
from json import JSONDecodeError
from typing import Any, Awaitable, Callable

from aiokafka import AIOKafkaConsumer

from analytics.infrastructure.messaging.kafka.events import CONSUMED_TOPICS

logger = logging.getLogger(__name__)
EventHandler = Callable[[str, dict[str, Any]], Awaitable[None]]


def _safe_json_deserializer(value: bytes) -> dict[str, Any]:
    try:
        decoded = json.loads(value.decode("utf-8"))
        return decoded if isinstance(decoded, dict) else {}
    except (UnicodeDecodeError, JSONDecodeError):
        logger.warning("Kafka message ignored because it is not valid JSON")
        return {}


class KafkaConsumerAdapter:
    def __init__(self, bootstrap_servers: str, consumer_group: str, handler: EventHandler):
        self._consumer = AIOKafkaConsumer(
            *CONSUMED_TOPICS,
            bootstrap_servers=bootstrap_servers,
            group_id=consumer_group,
            value_deserializer=_safe_json_deserializer,
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
                try:
                    await self._handler(message.topic, message.value)
                except Exception:
                    logger.exception("Kafka event handling failed for topic: %s", message.topic)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Kafka consumer loop stopped unexpectedly")
