from datetime import datetime

from analytics.application.outboundservices.analytics_event_publisher import AnalyticsEventPublisher
from analytics.domain.model.commands.create_device_identification_command import CreateDeviceIdentificationCommand
from analytics.domain.model.entities.device_identification_result import DeviceIdentificationResult
from analytics.domain.repositories.device_identification_result_repository import DeviceIdentificationResultRepository
from analytics.domain.services.analytics_rule_service import AnalyticsRuleService


class DeviceIdentificationCommandService:
    def __init__(
        self,
        repository: DeviceIdentificationResultRepository,
        rule_service: AnalyticsRuleService,
        event_publisher: AnalyticsEventPublisher,
    ):
        self._repository = repository
        self._rule_service = rule_service
        self._event_publisher = event_publisher

    async def create(self, command: CreateDeviceIdentificationCommand) -> DeviceIdentificationResult:
        now = datetime.utcnow()
        predicted_type = command.predicted_device_type
        confidence = command.confidence_score
        if predicted_type is None or confidence is None:
            predicted_type, confidence = self._rule_service.identify_device_type(command.average_daily_kwh)
        result = DeviceIdentificationResult(
            user_id=command.user_id,
            device_id=command.device_id,
            predicted_device_type=predicted_type,
            confidence_score=round(float(confidence), 2),
            status=command.status,
            analyzed_at=now,
            created_at=now,
        )
        saved = await self._repository.save(result)
        await self._event_publisher.publish_device_identified(saved)
        return saved
