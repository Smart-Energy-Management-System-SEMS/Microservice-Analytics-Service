from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Recommendation:
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
    id: Optional[str] = None
