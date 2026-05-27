from analytics.domain.model.entities.recommendation import Recommendation
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.domain.repositories.recommendation_repository import RecommendationRepository


class RecommendationQueryService:
    def __init__(self, repository: RecommendationRepository):
        self._repository = repository

    async def get_by_user(self, query: GetByUserQuery) -> list[Recommendation]:
        return await self._repository.find_by_user_id(query.user_id)
