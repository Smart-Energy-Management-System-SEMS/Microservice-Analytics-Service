from datetime import datetime

from analytics.application.outboundservices.analytics_event_publisher import AnalyticsEventPublisher
from analytics.domain.model.commands.create_anomaly_command import CreateAnomalyCommand
from analytics.domain.model.entities.anomaly import Anomaly
from analytics.domain.repositories.anomaly_repository import AnomalyRepository
from analytics.domain.services.analytics_rule_service import AnalyticsRuleService


class AnomalyCommandService:
    def __init__(
        self,
        repository: AnomalyRepository,
        rule_service: AnalyticsRuleService,
        event_publisher: AnalyticsEventPublisher,
    ):
        self._repository = repository
        self._rule_service = rule_service
        self._event_publisher = event_publisher

    async def create(self, command: CreateAnomalyCommand) -> Anomaly:
        anomaly = self._build_anomaly(command)
        saved = await self._repository.save(anomaly)
        await self._event_publisher.publish_anomaly_detected(saved)
        return saved

    async def detect_and_create(self, command: CreateAnomalyCommand) -> Anomaly | None:
        is_anomaly, _, _, _, _ = self._rule_service.detect_anomaly(
            command.actual_kwh,
            command.expected_kwh,
            command.historical_kwh,
            command.threshold_percentage,
        )
        if not is_anomaly:
            return None
        return await self.create(command)

    async def resolve(self, anomaly_id: str) -> Anomaly | None:
        return await self._repository.mark_resolved(anomaly_id)

    def _build_anomaly(self, command: CreateAnomalyCommand) -> Anomaly:
        _, calculated_type, severity, expected, deviation = self._rule_service.detect_anomaly(
            command.actual_kwh,
            command.expected_kwh,
            command.historical_kwh,
            command.threshold_percentage,
        )
        now = datetime.utcnow()
        anomaly_type = command.anomaly_type or calculated_type
        description = command.description or (
            f"Consumption deviated {deviation}% from expected usage for device {command.device_id}."
        )
        anomaly = Anomaly(
            user_id=command.user_id,
            device_id=command.device_id,
            anomaly_type=anomaly_type,
            description=description,
            severity=severity,
            status="open",
            actual_kwh=round(float(command.actual_kwh), 2),
            expected_kwh=expected,
            deviation_percentage=deviation,
            detected_at=now,
            resolved_at=None,
            created_at=now,
        )
        return anomaly
