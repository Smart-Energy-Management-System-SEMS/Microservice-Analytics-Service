"""Command Service for the Anomaly aggregate.

Application layer within the DDD + CQRS architecture.
This is the "write" side (Command) of the anomaly use case: it orchestrates
the domain (business rules), persists the result through the repository, and
publishes the corresponding integration event.

It holds no business rules of its own; the calculations are delegated to
``AnalyticsRuleService`` (a domain service) to respect the single
responsibility principle.
"""

from datetime import datetime

# Injected dependencies: event publisher, input command, domain entity,
# repository contract, and the rules service.
from analytics.application.outboundservices.analytics_event_publisher import AnalyticsEventPublisher
from analytics.domain.model.commands.create_anomaly_command import CreateAnomalyCommand
from analytics.domain.model.entities.anomaly import Anomaly
from analytics.domain.repositories.anomaly_repository import AnomalyRepository
from analytics.domain.services.analytics_rule_service import AnalyticsRuleService


class AnomalyCommandService:
    """Coordinates the creation and resolution of consumption anomalies."""

    def __init__(
        self,
        repository: AnomalyRepository,
        rule_service: AnalyticsRuleService,
        event_publisher: AnalyticsEventPublisher,
    ):
        # Dependency injection (DIP): we depend on abstractions, not on
        # concrete implementations, which makes the service easy to test.
        self._repository = repository
        self._rule_service = rule_service
        self._event_publisher = event_publisher

    async def create(self, command: CreateAnomalyCommand) -> Anomaly:
        """Build, persist, and publish an anomaly from the given command."""
        # 1) Build the domain entity by applying the business rules.
        anomaly = self._build_anomaly(command)
        # 2) Persist it through the repository (returns the entity with its id).
        saved = await self._repository.save(anomaly)
        # 3) Notify the rest of the system via an integration event.
        await self._event_publisher.publish_anomaly_detected(saved)
        return saved

    async def detect_and_create(self, command: CreateAnomalyCommand) -> Anomaly | None:
        """Create the anomaly ONLY if the domain rules detect one.

        Useful for automated flows (e.g. when consuming Kafka events), where
        we must first decide whether an anomaly actually exists.
        """
        # Ask the domain service whether the data represents an anomaly.
        is_anomaly, _, _, _, _ = self._rule_service.detect_anomaly(
            command.actual_kwh,
            command.expected_kwh,
            command.historical_kwh,
            command.threshold_percentage,
        )
        # If there is no anomaly, nothing is created (early return).
        if not is_anomaly:
            return None
        return await self.create(command)

    async def resolve(self, anomaly_id: str) -> Anomaly | None:
        """Mark an existing anomaly as resolved."""
        return await self._repository.mark_resolved(anomaly_id)

    def _build_anomaly(self, command: CreateAnomalyCommand) -> Anomaly:
        """Private factory: turn the command into an Anomaly entity.

        Computes type, severity, expected value, and deviation using the
        domain rules, while honoring any values already provided in the command.
        """
        # The rules service returns the values derived from the analysis.
        _, calculated_type, severity, expected, deviation = self._rule_service.detect_anomaly(
            command.actual_kwh,
            command.expected_kwh,
            command.historical_kwh,
            command.threshold_percentage,
        )
        now = datetime.utcnow()
        # Prefer the value provided in the command; otherwise use the computed one.
        anomaly_type = command.anomaly_type or calculated_type
        # Default description generated automatically if none was provided.
        description = command.description or (
            f"Consumption deviated {deviation}% from expected usage for device {command.device_id}."
        )
        # Build the entity with an initial "open" status.
        anomaly = Anomaly(
            user_id=command.user_id,
            device_id=command.device_id,
            anomaly_type=anomaly_type,
            description=description,
            severity=severity,
            status="open",
            actual_kwh=round(float(command.actual_kwh), 2),  # rounded to 2 decimals
            expected_kwh=expected,
            deviation_percentage=deviation,
            detected_at=now,
            resolved_at=None,  # not resolved yet
            created_at=now,
        )
        return anomaly
