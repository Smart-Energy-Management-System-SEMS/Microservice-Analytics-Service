from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class RankingSourceItem:
    device_id: str
    device_name: str
    total_kwh: float


@dataclass(slots=True)
class CreateConsumptionRankingCommand:
    user_id: str
    period_type: str
    period_start: datetime
    period_end: datetime
    devices: list[RankingSourceItem]
    tariff_per_kwh: float = 0.65
    currency: str = "USD"
