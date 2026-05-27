from abc import ABC, abstractmethod

from analytics.domain.model.entities.consumption_ranking import ConsumptionRanking


class ConsumptionRankingRepository(ABC):
    @abstractmethod
    async def save(self, ranking: ConsumptionRanking) -> ConsumptionRanking:
        raise NotImplementedError

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> list[ConsumptionRanking]:
        raise NotImplementedError
