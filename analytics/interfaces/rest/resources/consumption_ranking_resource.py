from datetime import datetime

from pydantic import BaseModel, Field


class RankingSourceItemRequest(BaseModel):
    device_id: str
    device_name: str
    total_kwh: float = Field(ge=0)


class CreateConsumptionRankingRequest(BaseModel):
    user_id: str
    period_type: str
    period_start: datetime
    period_end: datetime
    devices: list[RankingSourceItemRequest]
    tariff_per_kwh: float = Field(default=0.65, ge=0)
    currency: str = "USD"


class RankingItemResponse(BaseModel):
    rank: int
    device_id: str
    device_name: str
    total_kwh: float
    estimated_amount: float
    percentage_of_total: float
    currency: str


class ConsumptionRankingResponse(BaseModel):
    id: str
    user_id: str
    period_type: str
    period_start: datetime
    period_end: datetime
    rankings: list[RankingItemResponse]
    generated_at: datetime
    created_at: datetime
