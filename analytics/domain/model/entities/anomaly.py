from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Anomaly:
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
    id: Optional[str] = None
