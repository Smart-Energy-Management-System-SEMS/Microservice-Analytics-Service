"""Command Service for the ConsumptionRanking aggregate.

Application layer (write side of CQRS). Generates the consumption ranking of
a user's devices over a period, delegating the ranking computation to the
domain rules service.
"""

from datetime import datetime

from analytics.application.outboundservices.analytics_event_publisher import AnalyticsEventPublisher
from analytics.domain.model.commands.create_consumption_ranking_command import CreateConsumptionRankingCommand
from analytics.domain.model.entities.consumption_ranking import ConsumptionRanking
from analytics.domain.repositories.consumption_ranking_repository import ConsumptionRankingRepository
from analytics.domain.services.analytics_rule_service import AnalyticsRuleService


class ConsumptionRankingCommandService:
    """Orchestrates the creation of the per-device consumption ranking."""

    def __init__(
        self,
        repository: ConsumptionRankingRepository,
        rule_service: AnalyticsRuleService,
        event_publisher: AnalyticsEventPublisher,
    ):
        # Injected dependencies (repository, rules, and event publisher).
        self._repository = repository
        self._rule_service = rule_service
        self._event_publisher = event_publisher

    async def create(self, command: CreateConsumptionRankingCommand) -> ConsumptionRanking:
        """Build, persist, and publish a consumption ranking."""
        now = datetime.utcnow()
        ranking = ConsumptionRanking(
            user_id=command.user_id,
            period_type=command.period_type,
            period_start=command.period_start,
            period_end=command.period_end,
            # The domain service sorts the devices and computes their positions.
            rankings=self._rule_service.build_ranking(command.devices, command.tariff_per_kwh, command.currency),
            generated_at=now,
            created_at=now,
        )
        # Persist and notify the "ranking generated" event.
        saved = await self._repository.save(ranking)
        await self._event_publisher.publish_consumption_ranking_generated(saved)
        return saved
