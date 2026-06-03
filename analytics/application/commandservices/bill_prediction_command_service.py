"""Command Service for the BillPrediction aggregate.

Application layer (write side of CQRS). Generates a user's bill prediction:
if the command does not carry the already-computed values, it estimates them
using the domain rules service, persists the result, and publishes the
integration event.
"""

from datetime import datetime

from analytics.application.outboundservices.analytics_event_publisher import AnalyticsEventPublisher
from analytics.domain.model.commands.create_bill_prediction_command import CreateBillPredictionCommand
from analytics.domain.model.entities.bill_prediction import BillPrediction
from analytics.domain.repositories.bill_prediction_repository import BillPredictionRepository
from analytics.domain.services.analytics_rule_service import AnalyticsRuleService


class BillPredictionCommandService:
    """Orchestrates the creation of bill predictions."""

    def __init__(
        self,
        repository: BillPredictionRepository,
        rule_service: AnalyticsRuleService,
        event_publisher: AnalyticsEventPublisher,
    ):
        # Dependencies injected through abstractions (repository, domain rules,
        # and event publisher).
        self._repository = repository
        self._rule_service = rule_service
        self._event_publisher = event_publisher

    async def create(self, command: CreateBillPredictionCommand) -> BillPrediction:
        """Compute (if needed), persist, and publish a bill prediction."""
        now = datetime.utcnow()

        # Estimated kWh: use the command's value or compute it from history.
        estimated_kwh = command.estimated_kwh
        if estimated_kwh is None:
            estimated_kwh = self._rule_service.estimate_kwh(command.historical_consumption_kwh)

        # Estimated amount: same as above; honor the given value or compute it
        # by multiplying the kWh by the tariff.
        estimated_amount = command.estimated_amount
        if estimated_amount is None:
            estimated_amount = self._rule_service.calculate_amount(estimated_kwh, command.tariff_per_kwh)

        # Build the domain entity with the period data.
        prediction = BillPrediction(
            user_id=command.user_id,
            prediction_year=command.prediction_year,
            prediction_month=command.prediction_month,
            period_start=command.period_start,
            period_end=command.period_end,
            estimated_kwh=round(float(estimated_kwh), 2),
            estimated_amount=round(float(estimated_amount), 2),
            currency=command.currency,
            tariff_used=command.tariff_per_kwh,
            error_margin_percentage=command.error_margin_percentage,
            generated_at=now,
            created_at=now,
        )
        # Persist and publish the "prediction generated" event.
        saved = await self._repository.save(prediction)
        await self._event_publisher.publish_bill_prediction_generated(saved)
        return saved
