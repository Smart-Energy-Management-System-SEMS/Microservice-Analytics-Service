from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class CreateBillPredictionCommand:
    user_id: str
    prediction_year: int
    prediction_month: int
    period_start: datetime
    period_end: datetime
    historical_consumption_kwh: list[float]
    tariff_per_kwh: float
    currency: str = "USD"
    estimated_kwh: float | None = None
    estimated_amount: float | None = None
    error_margin_percentage: float = 10.0
