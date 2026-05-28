from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from analytics.infrastructure.configuration.settings import get_settings

settings = get_settings()


class CreateAnomalyRequest(BaseModel):
    user_id: str
    device_id: str
    actual_kwh: float = Field(ge=0)
    expected_kwh: Optional[float] = Field(default=None, ge=0)
    historical_kwh: list[float] = Field(default_factory=list)
    threshold_percentage: float = Field(default=settings.anomaly_threshold_percentage, ge=0)
    anomaly_type: Optional[str] = None
    description: Optional[str] = None


class AnomalyResponse(BaseModel):
    id: str
    user_id: str
    device_id: str
    anomaly_type: str
    description: str
    severity: str
    status: str
    actual_kwh: float
    expected_kwh: float
    deviation_percentage: float
    detected_at: datetime
    resolved_at: Optional[datetime]
    created_at: datetime
