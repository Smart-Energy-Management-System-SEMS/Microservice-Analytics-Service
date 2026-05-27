from dataclasses import dataclass


@dataclass(slots=True)
class RankingItem:
    rank: int
    device_id: str
    device_name: str
    total_kwh: float
    estimated_amount: float
    percentage_of_total: float
    currency: str
