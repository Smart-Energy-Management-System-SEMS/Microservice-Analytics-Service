from abc import ABC, abstractmethod

from analytics.domain.model.entities.recommendation import Recommendation


class RecommendationRepository(ABC):
    @abstractmethod
    async def save(self, recommendation: Recommendation) -> Recommendation:
        raise NotImplementedError

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> list[Recommendation]:
        raise NotImplementedError

    @abstractmethod
    async def mark_applied(self, recommendation_id: str) -> Recommendation | None:
        raise NotImplementedError
