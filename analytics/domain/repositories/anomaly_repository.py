from abc import ABC, abstractmethod

from analytics.domain.model.entities.anomaly import Anomaly


class AnomalyRepository(ABC):
    @abstractmethod
    async def save(self, anomaly: Anomaly) -> Anomaly:
        raise NotImplementedError

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> list[Anomaly]:
        raise NotImplementedError

    @abstractmethod
    async def mark_resolved(self, anomaly_id: str) -> Anomaly | None:
        raise NotImplementedError
