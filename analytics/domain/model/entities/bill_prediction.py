from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class BillPrediction:
    user_id: str
    prediction_year: int
    prediction_month: int
    period_start: datetime
    period_end: datetime
    estimated_kwh: float
    estimated_amount: float
    currency: str
    tariff_used: float
    error_margin_percentage: float
    generated_at: datetime
    created_at: datetime
    id: Optional[str] = None
