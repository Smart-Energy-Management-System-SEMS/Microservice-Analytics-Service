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
    def __init__(
        self,
        bootstrap_servers: str,
        security_protocol: str = "PLAINTEXT",
        sasl_mechanism: str = "",
        sasl_username: str = "",
        sasl_password: str = "",
    ):
        kafka_params: dict[str, Any] = {
            "bootstrap_servers": bootstrap_servers,
            "value_serializer": lambda value: json.dumps(value, default=_json_default).encode("utf-8"),
        }
        if security_protocol:
            kafka_params["security_protocol"] = security_protocol
        if sasl_mechanism:
            kafka_params["sasl_mechanism"] = sasl_mechanism
        if sasl_username:
            kafka_params["sasl_plain_username"] = sasl_username
        if sasl_password:
            kafka_params["sasl_plain_password"] = sasl_password

        self._producer = AIOKafkaProducer(
            **kafka_params,
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
