import json
import logging
from datetime import date, datetime
from typing import Any

from aiokafka import AIOKafkaProducer

logger = logging.getLogger(__name__)


def _json_default(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


class KafkaProducerAdapter:
    def __init__(self, bootstrap_servers: str):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda value: json.dumps(value, default=_json_default).encode("utf-8"),
        )
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        await self._producer.start()
        self._started = True
        logger.info("Kafka producer started")

    async def stop(self) -> None:
        if self._started:
            await self._producer.stop()
            self._started = False
            logger.info("Kafka producer stopped")

    async def publish(self, topic: str, payload: dict[str, Any]) -> None:
        if not self._started:
            logger.warning("Kafka producer is not started; event skipped: %s", topic)
            return
        await self._producer.send_and_wait(topic, payload)
