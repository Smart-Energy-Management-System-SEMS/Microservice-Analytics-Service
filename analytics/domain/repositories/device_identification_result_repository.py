from abc import ABC, abstractmethod

from analytics.domain.model.entities.device_identification_result import DeviceIdentificationResult


class DeviceIdentificationResultRepository(ABC):
    @abstractmethod
    async def save(self, result: DeviceIdentificationResult) -> DeviceIdentificationResult:
        raise NotImplementedError

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> list[DeviceIdentificationResult]:
        raise NotImplementedError
