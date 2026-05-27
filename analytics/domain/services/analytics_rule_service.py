from statistics import mean

from analytics.domain.model.commands.create_consumption_ranking_command import RankingSourceItem
from analytics.domain.model.valueobjects.ranking_item import RankingItem


class AnalyticsRuleService:
    def identify_device_type(self, average_daily_kwh: float | None) -> tuple[str, float]:
        if average_daily_kwh is None:
            return "unknown", 0.5
        if average_daily_kwh >= 12:
            return "hvac_or_heavy_appliance", 0.78
        if average_daily_kwh >= 5:
            return "refrigeration_or_laundry", 0.72
        if average_daily_kwh >= 1.5:
            return "lighting_or_entertainment", 0.68
        return "low_consumption_device", 0.65

    def estimate_kwh(self, historical_consumption_kwh: list[float]) -> float:
        values = [value for value in historical_consumption_kwh if value >= 0]
        if not values:
            return 0.0
        recent_values = values[-6:]
        return round(mean(recent_values), 2)

    def calculate_amount(self, kwh: float, tariff_per_kwh: float) -> float:
        return round(max(kwh, 0) * max(tariff_per_kwh, 0), 2)

    def recommendation_from_usage(
        self,
        current_kwh: float | None,
        average_kwh: float | None,
        tariff_per_kwh: float,
    ) -> tuple[str, str, str, float, float]:
        current = current_kwh or 0.0
        average = average_kwh or 0.0
        if current > 0 and average > 0 and current > average * 1.2:
            saving_kwh = round((current - average) * 0.6, 2)
            saving_amount = self.calculate_amount(saving_kwh, tariff_per_kwh)
            return (
                "high_consumption_reduction",
                "Reduce high consumption",
                "Current consumption is above the historical average. Review schedules and standby usage.",
                saving_kwh,
                saving_amount,
            )
        saving_kwh = round(current * 0.08, 2) if current > 0 else 0.0
        saving_amount = self.calculate_amount(saving_kwh, tariff_per_kwh)
        return (
            "efficiency_improvement",
            "Improve energy efficiency",
            "Apply basic efficiency habits such as turning devices off when not in use.",
            saving_kwh,
            saving_amount,
        )

    def detect_anomaly(
        self,
        actual_kwh: float,
        expected_kwh: float | None,
        historical_kwh: list[float] | None,
        threshold_percentage: float,
    ) -> tuple[bool, str, str, float, float]:
        expected = expected_kwh
        if expected is None:
            values = [value for value in (historical_kwh or []) if value >= 0]
            expected = mean(values[-10:]) if values else actual_kwh
        expected = round(float(expected), 2)
        if expected <= 0:
            deviation = 100.0 if actual_kwh > 0 else 0.0
        else:
            deviation = round(((actual_kwh - expected) / expected) * 100, 2)
        is_anomaly = abs(deviation) >= threshold_percentage
        severity = "critical" if abs(deviation) >= 75 else "high" if abs(deviation) >= 50 else "medium"
        anomaly_type = "consumption_spike" if deviation > 0 else "consumption_drop"
        return is_anomaly, anomaly_type, severity, expected, deviation

    def build_ranking(
        self,
        devices: list[RankingSourceItem],
        tariff_per_kwh: float,
        currency: str,
    ) -> list[RankingItem]:
        sorted_devices = sorted(devices, key=lambda item: item.total_kwh, reverse=True)
        total = sum(max(item.total_kwh, 0) for item in sorted_devices)
        rankings: list[RankingItem] = []
        for index, device in enumerate(sorted_devices, start=1):
            total_kwh = round(max(device.total_kwh, 0), 2)
            percentage = round((total_kwh / total) * 100, 2) if total > 0 else 0.0
            rankings.append(
                RankingItem(
                    rank=index,
                    device_id=device.device_id,
                    device_name=device.device_name,
                    total_kwh=total_kwh,
                    estimated_amount=self.calculate_amount(total_kwh, tariff_per_kwh),
                    percentage_of_total=percentage,
                    currency=currency,
                )
            )
        return rankings
