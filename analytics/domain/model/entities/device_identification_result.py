from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class DeviceIdentificationResult:
    user_id: str
    device_id: str
    predicted_device_type: str
    confidence_score: float
    status: str
    analyzed_at: datetime
    created_at: datetime
    id: Optional[str] = None
