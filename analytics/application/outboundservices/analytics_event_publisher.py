from dataclasses import asdict, is_dataclass
from typing import Any

from analytics.domain.model.entities.anomaly import Anomaly
from analytics.domain.model.entities.bill_prediction import BillPrediction
from analytics.domain.model.entities.consumption_ranking import ConsumptionRanking
from analytics.domain.model.entities.device_identification_result import DeviceIdentificationResult
from analytics.domain.model.entities.recommendation import Recommendation
from analytics.infrastructure.messaging.kafka import events
from analytics.infrastructure.messaging.kafka.kafka_producer import KafkaProducerAdapter


class AnalyticsEventPublisher:
    def __init__(self, producer: KafkaProducerAdapter | None):
        self._producer = producer

    async def publish_device_identified(self, result: DeviceIdentificationResult) -> None:
        await self._publish(events.ANALYTICS_DEVICE_IDENTIFIED, result)

    async def publish_bill_prediction_generated(self, prediction: BillPrediction) -> None:
        await self._publish(events.ANALYTICS_BILL_PREDICTION_GENERATED, prediction)

    async def publish_recommendation_generated(self, recommendation: Recommendation) -> None:
        await self._publish(events.ANALYTICS_RECOMMENDATION_GENERATED, recommendation)

    async def publish_anomaly_detected(self, anomaly: Anomaly) -> None:
        await self._publish(events.ANALYTICS_ANOMALY_DETECTED, anomaly)

    async def publish_consumption_ranking_generated(self, ranking: ConsumptionRanking) -> None:
        await self._publish(events.ANALYTICS_CONSUMPTION_RANKING_GENERATED, ranking)

    async def _publish(self, topic: str, entity: Any) -> None:
        if self._producer is None:
            return
        payload = asdict(entity) if is_dataclass(entity) else dict(entity)
        await self._producer.publish(topic, payload)
