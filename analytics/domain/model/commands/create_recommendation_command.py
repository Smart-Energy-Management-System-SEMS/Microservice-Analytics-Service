from dataclasses import dataclass


@dataclass(slots=True)
class CreateRecommendationCommand:
    user_id: str
    device_id: str | None = None
    recommendation_type: str | None = None
    current_kwh: float | None = None
    average_kwh: float | None = None
    estimated_saving_kwh: float | None = None
    tariff_per_kwh: float = 0.65
    currency: str = "USD"
