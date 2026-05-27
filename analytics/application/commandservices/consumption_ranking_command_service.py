from datetime import datetime

from analytics.application.outboundservices.analytics_event_publisher import AnalyticsEventPublisher
from analytics.domain.model.commands.create_consumption_ranking_command import CreateConsumptionRankingCommand
from analytics.domain.model.entities.consumption_ranking import ConsumptionRanking
from analytics.domain.repositories.consumption_ranking_repository import ConsumptionRankingRepository
from analytics.domain.services.analytics_rule_service import AnalyticsRuleService


class ConsumptionRankingCommandService:
    def __init__(
        self,
        repository: ConsumptionRankingRepository,
        rule_service: AnalyticsRuleService,
        event_publisher: AnalyticsEventPublisher,
    ):
        self._repository = repository
        self._rule_service = rule_service
        self._event_publisher = event_publisher

    async def create(self, command: CreateConsumptionRankingCommand) -> ConsumptionRanking:
        now = datetime.utcnow()
        ranking = ConsumptionRanking(
            user_id=command.user_id,
            period_type=command.period_type,
            period_start=command.period_start,
            period_end=command.period_end,
            rankings=self._rule_service.build_ranking(command.devices, command.tariff_per_kwh, command.currency),
            generated_at=now,
            created_at=now,
        )
        saved = await self._repository.save(ranking)
        await self._event_publisher.publish_consumption_ranking_generated(saved)
        return saved
