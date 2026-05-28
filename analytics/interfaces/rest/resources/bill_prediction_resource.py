from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from analytics.infrastructure.configuration.settings import get_settings

settings = get_settings()


class CreateBillPredictionRequest(BaseModel):
    user_id: str
    prediction_year: int = Field(ge=2000, le=2100)
    prediction_month: int = Field(ge=1, le=12)
    period_start: datetime
    period_end: datetime
    historical_consumption_kwh: list[float] = Field(default_factory=list)
    tariff_per_kwh: float = Field(default=settings.default_tariff_per_kwh, ge=0)
    currency: str = settings.default_currency
    estimated_kwh: Optional[float] = Field(default=None, ge=0)
    estimated_amount: Optional[float] = Field(default=None, ge=0)
    error_margin_percentage: float = Field(default=10.0, ge=0)


class BillPredictionResponse(BaseModel):
    id: str
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
