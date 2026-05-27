from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from analytics.domain.model.valueobjects.ranking_item import RankingItem


@dataclass(slots=True)
class ConsumptionRanking:
    user_id: str
    period_type: str
    period_start: datetime
    period_end: datetime
    rankings: list[RankingItem]
    generated_at: datetime
    created_at: datetime
    id: Optional[str] = None
