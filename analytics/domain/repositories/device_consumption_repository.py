from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from analytics.domain.model.entities.device_consumption import DeviceConsumption


@dataclass(slots=True)
class DeviceConsumptionSummary:
    device_id: str
    total_kwh: float
    device_name: str


class DeviceConsumptionRepository(ABC):
    @abstractmethod
    async def save(self, reading: DeviceConsumption) -> DeviceConsumption:
        raise NotImplementedError

    @abstractmethod
    async def find_recent_by_device(
        self,
        user_id: str,
        device_id: str,
        limit: int,
    ) -> list[DeviceConsumption]:
        raise NotImplementedError

    @abstractmethod
    async def summarize_devices_for_period(
        self,
        user_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> list[DeviceConsumptionSummary]:
        raise NotImplementedError

    @abstractmethod
    async def find_daily_user_totals_for_period(
        self,
        user_id: str,
        period_start: datetime,
        period_end: datetime,
    ) -> list[float]:
        raise NotImplementedError
