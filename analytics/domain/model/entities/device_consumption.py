from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class DeviceConsumption:
    user_id: str
    device_id: str
    energy_kwh: float
    measured_at: datetime
    created_at: datetime
    meter_id: Optional[str] = None
    power_watts: Optional[float] = None
    estimated_cost: Optional[float] = None
    currency: Optional[str] = None
    reading_type: Optional[str] = None
    id: Optional[str] = None
