from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from analytics.infrastructure.configuration.settings import get_settings

settings = get_settings()


class CreateRecommendationRequest(BaseModel):
    user_id: str
    device_id: Optional[str] = None
    recommendation_type: Optional[str] = None
    current_kwh: Optional[float] = Field(default=None, ge=0)
    average_kwh: Optional[float] = Field(default=None, ge=0)
    estimated_saving_kwh: Optional[float] = Field(default=None, ge=0)
    tariff_per_kwh: float = Field(default=settings.default_tariff_per_kwh, ge=0)
    currency: str = settings.default_currency


class RecommendationResponse(BaseModel):
    id: str
    user_id: str
    device_id: Optional[str]
    recommendation_type: str
    title: str
    description: str
    estimated_saving_kwh: float
    estimated_saving_amount: float
    currency: str
    status: str
    generated_at: datetime
    applied_at: Optional[datetime]
    created_at: datetime
