from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateDeviceIdentificationRequest(BaseModel):
    user_id: str
    device_id: str
    average_daily_kwh: Optional[float] = Field(default=None, ge=0)
    predicted_device_type: Optional[str] = None
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1)
    status: str = "completed"


class DeviceIdentificationResponse(BaseModel):
    id: str
    user_id: str
    device_id: str
    predicted_device_type: str
    confidence_score: float
    status: str
    analyzed_at: datetime
    created_at: datetime
