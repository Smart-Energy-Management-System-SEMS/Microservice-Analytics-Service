"""Outbound Service: analytics event publisher.

Application layer. Acts as a Facade over the Kafka producer: it exposes one
method per domain event type and is responsible for serializing the entity to
a dictionary before sending it to the broker.

It shields the Command Services from the messaging details (Kafka), so the
domain does not depend on the concrete transport technology.
"""

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
    """Publishes the integration events of the analytics service."""

    def __init__(self, producer: KafkaProducerAdapter | None):
        # The producer is optional (None): this allows disabling messaging in
        # test environments or when Kafka is not available.
        self._producer = producer

    async def publish_device_identified(self, result: DeviceIdentificationResult) -> None:
        """Publish the device-identified event."""
        await self._publish(events.ANALYTICS_DEVICE_IDENTIFIED, result)

    async def publish_bill_prediction_generated(self, prediction: BillPrediction) -> None:
        """Publish the bill-prediction-generated event."""
        await self._publish(events.ANALYTICS_BILL_PREDICTION_GENERATED, prediction)

    async def publish_recommendation_generated(self, recommendation: Recommendation) -> None:
        """Publish the recommendation-generated event."""
        await self._publish(events.ANALYTICS_RECOMMENDATION_GENERATED, recommendation)

    async def publish_anomaly_detected(self, anomaly: Anomaly) -> None:
        """Publish the anomaly-detected event."""
        await self._publish(events.ANALYTICS_ANOMALY_DETECTED, anomaly)

    async def publish_consumption_ranking_generated(self, ranking: ConsumptionRanking) -> None:
        """Publish the consumption-ranking-generated event."""
        await self._publish(events.ANALYTICS_CONSUMPTION_RANKING_GENERATED, ranking)

    async def _publish(self, topic: str, entity: Any) -> None:
        """Shared private method: serialize the entity and send it to the topic."""
        # If no producer is configured, publish nothing (safe no-op).
        if self._producer is None:
            return
        # Convert the entity to a dict: use asdict for dataclasses, else dict().
        payload = asdict(entity) if is_dataclass(entity) else dict(entity)
        await self._producer.publish(topic, payload)
