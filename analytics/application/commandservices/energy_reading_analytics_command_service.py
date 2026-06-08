import calendar
from datetime import datetime, timedelta

from analytics.application.commandservices.anomaly_command_service import AnomalyCommandService
from analytics.application.commandservices.bill_prediction_command_service import BillPredictionCommandService
from analytics.application.commandservices.consumption_ranking_command_service import ConsumptionRankingCommandService
from analytics.application.commandservices.recommendation_command_service import RecommendationCommandService
from analytics.domain.model.commands.create_anomaly_command import CreateAnomalyCommand
from analytics.domain.model.commands.create_bill_prediction_command import CreateBillPredictionCommand
from analytics.domain.model.commands.create_consumption_ranking_command import (
    CreateConsumptionRankingCommand,
    RankingSourceItem,
)
from analytics.domain.model.commands.create_recommendation_command import CreateRecommendationCommand
from analytics.domain.model.entities.device_consumption import DeviceConsumption
from analytics.domain.repositories.device_consumption_repository import DeviceConsumptionRepository
from analytics.domain.services.analytics_rule_service import AnalyticsRuleService


class EnergyReadingAnalyticsCommandService:
    """Consumes a reading and refreshes all analytics artifacts derived from it."""

    def __init__(
        self,
        repository: DeviceConsumptionRepository,
        anomaly_command_service: AnomalyCommandService,
        bill_prediction_command_service: BillPredictionCommandService,
        recommendation_command_service: RecommendationCommandService,
        consumption_ranking_command_service: ConsumptionRankingCommandService,
        rule_service: AnalyticsRuleService,
        default_tariff_per_kwh: float,
        default_currency: str,
    ):
        self._repository = repository
        self._anomaly_command_service = anomaly_command_service
        self._bill_prediction_command_service = bill_prediction_command_service
        self._recommendation_command_service = recommendation_command_service
        self._consumption_ranking_command_service = consumption_ranking_command_service
        self._rule_service = rule_service
        self._default_tariff_per_kwh = default_tariff_per_kwh
        self._default_currency = default_currency

    async def process(self, reading: DeviceConsumption) -> None:
        prior_history = await self._repository.find_recent_by_device(
            reading.user_id,
            reading.device_id,
            limit=10,
        )
        await self._repository.save(reading)

        historical_kwh = [item.energy_kwh for item in prior_history]
        await self._anomaly_command_service.detect_and_create(
            CreateAnomalyCommand(
                user_id=reading.user_id,
                device_id=reading.device_id,
                actual_kwh=reading.energy_kwh,
                expected_kwh=None,
                historical_kwh=historical_kwh,
            )
        )

        average_kwh = (
            round(sum(historical_kwh) / len(historical_kwh), 2)
            if historical_kwh
            else reading.energy_kwh
        )
        await self._recommendation_command_service.create(
            CreateRecommendationCommand(
                user_id=reading.user_id,
                device_id=reading.device_id,
                current_kwh=reading.energy_kwh,
                average_kwh=average_kwh,
                tariff_per_kwh=self._default_tariff_per_kwh,
                currency=reading.currency or self._default_currency,
            )
        )

        month_start = reading.measured_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month_start = self._next_month_start(month_start)
        month_end = next_month_start - timedelta(microseconds=1)

        device_totals = await self._repository.summarize_devices_for_period(
            reading.user_id,
            month_start,
            next_month_start,
        )
        if device_totals:
            await self._consumption_ranking_command_service.create(
                CreateConsumptionRankingCommand(
                    user_id=reading.user_id,
                    period_type="monthly",
                    period_start=month_start,
                    period_end=month_end,
                    devices=[
                        RankingSourceItem(
                            device_id=item.device_id,
                            device_name=item.device_name,
                            total_kwh=item.total_kwh,
                        )
                        for item in device_totals
                    ],
                    tariff_per_kwh=self._default_tariff_per_kwh,
                    currency=reading.currency or self._default_currency,
                )
            )

        daily_totals = await self._repository.find_daily_user_totals_for_period(
            reading.user_id,
            month_start,
            next_month_start,
        )
        if daily_totals:
            days_in_month = calendar.monthrange(reading.measured_at.year, reading.measured_at.month)[1]
            elapsed_days = max(1, reading.measured_at.day)
            consumed_so_far = round(sum(daily_totals), 2)
            projected_kwh = round((consumed_so_far / elapsed_days) * days_in_month, 2)
            await self._bill_prediction_command_service.create(
                CreateBillPredictionCommand(
                    user_id=reading.user_id,
                    prediction_year=reading.measured_at.year,
                    prediction_month=reading.measured_at.month,
                    period_start=month_start,
                    period_end=month_end,
                    historical_consumption_kwh=daily_totals,
                    tariff_per_kwh=self._default_tariff_per_kwh,
                    currency=reading.currency or self._default_currency,
                    estimated_kwh=projected_kwh,
                    estimated_amount=self._rule_service.calculate_amount(
                        projected_kwh,
                        self._default_tariff_per_kwh,
                    ),
                )
            )

    @staticmethod
    def _next_month_start(value: datetime) -> datetime:
        if value.month == 12:
            return value.replace(year=value.year + 1, month=1)
        return value.replace(month=value.month + 1)
