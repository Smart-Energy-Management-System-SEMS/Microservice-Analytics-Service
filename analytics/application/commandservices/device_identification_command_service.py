"""Command Service for DeviceIdentificationResult.

Application layer (write side of CQRS). Records the result of identifying
which device type corresponds to a consumption pattern: if the command does
not carry a prediction, it is inferred via the domain rules service from the
average daily consumption.
"""

from datetime import datetime

from analytics.application.outboundservices.analytics_event_publisher import AnalyticsEventPublisher
from analytics.domain.model.commands.create_device_identification_command import CreateDeviceIdentificationCommand
from analytics.domain.model.entities.device_identification_result import DeviceIdentificationResult
from analytics.domain.repositories.device_identification_result_repository import DeviceIdentificationResultRepository
from analytics.domain.services.analytics_rule_service import AnalyticsRuleService


class DeviceIdentificationCommandService:
    """Orchestrates the recording of device identification results."""

    def __init__(
        self,
        repository: DeviceIdentificationResultRepository,
        rule_service: AnalyticsRuleService,
        event_publisher: AnalyticsEventPublisher,
    ):
        # Injected dependencies (repository, rules, and event publisher).
        self._repository = repository
        self._rule_service = rule_service
        self._event_publisher = event_publisher

    async def create(self, command: CreateDeviceIdentificationCommand) -> DeviceIdentificationResult:
        """Determine (if needed), persist, and publish an identification result."""
        now = datetime.utcnow()
        predicted_type = command.predicted_device_type
        confidence = command.confidence_score
        # If the type or confidence is missing, infer them via the domain rules.
        if predicted_type is None or confidence is None:
            predicted_type, confidence = self._rule_service.identify_device_type(command.average_daily_kwh)

        # Build the entity holding the identification result.
        result = DeviceIdentificationResult(
            user_id=command.user_id,
            device_id=command.device_id,
            predicted_device_type=predicted_type,
            confidence_score=round(float(confidence), 2),  # rounded confidence
            status=command.status,
            analyzed_at=now,
            created_at=now,
        )
        # Persist and publish the "device identified" event.
        saved = await self._repository.save(result)
        await self._event_publisher.publish_device_identified(saved)
        return saved
