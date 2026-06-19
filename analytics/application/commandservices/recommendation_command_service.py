"""Command Service for the Recommendation aggregate.

Application layer (write side of CQRS). Generates energy-saving recommendations
from current consumption vs. the average, and allows marking them as applied.
The saving computation is performed by the domain rules service.
"""

from datetime import datetime

from analytics.application.outboundservices.analytics_event_publisher import AnalyticsEventPublisher
from analytics.domain.model.commands.create_recommendation_command import CreateRecommendationCommand
from analytics.domain.model.entities.recommendation import Recommendation
from analytics.domain.repositories.recommendation_repository import RecommendationRepository
from analytics.domain.services.analytics_rule_service import AnalyticsRuleService


class RecommendationCommandService:
    """Orchestrates the creation and application of saving recommendations."""

    def __init__(
        self,
        repository: RecommendationRepository,
        rule_service: AnalyticsRuleService,
        event_publisher: AnalyticsEventPublisher,
    ):
        # Injected dependencies (repository, rules, and event publisher).
        self._repository = repository
        self._rule_service = rule_service
        self._event_publisher = event_publisher

    async def create(self, command: CreateRecommendationCommand) -> Recommendation:
        """Build, persist, and publish a saving recommendation."""
        # The domain rules derive type, title, description, and estimated saving.
        recommendation_type, title, description, saving_kwh, saving_amount = self._rule_service.recommendation_from_usage(
            command.current_kwh,
            command.average_kwh,
            command.tariff_per_kwh,
        )
        # If the command specifies a concrete type, it takes precedence.
        if command.recommendation_type:
            recommendation_type = command.recommendation_type
        # If the command carries a kWh saving, recompute its associated amount.
        if command.estimated_saving_kwh is not None:
            saving_kwh = command.estimated_saving_kwh
            saving_amount = self._rule_service.calculate_amount(saving_kwh, command.tariff_per_kwh)

        now = datetime.utcnow()
        # Entity created with an initial "pending" status (not applied yet).
        recommendation = Recommendation(
            user_id=command.user_id,
            device_id=command.device_id,
            recommendation_type=recommendation_type,
            title=title,
            description=description,
            estimated_saving_kwh=round(float(saving_kwh), 2),
            estimated_saving_amount=round(float(saving_amount), 2),
            currency=command.currency,
            status="pending",
            generated_at=now,
            applied_at=None,  # filled in once the user applies it
            created_at=now,
        )
        # Persist and publish the "recommendation generated" event.
        saved = await self._repository.save(recommendation)
        await self._event_publisher.publish_recommendation_generated(saved)
        return saved

    async def apply(self, recommendation_id: str) -> Recommendation | None:
        """Mark an existing recommendation as applied by the user."""
        return await self._repository.mark_applied(recommendation_id)
