from analytics.domain.model.entities.consumption_ranking import ConsumptionRanking
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.domain.repositories.consumption_ranking_repository import ConsumptionRankingRepository


class ConsumptionRankingQueryService:
    def __init__(self, repository: ConsumptionRankingRepository):
        self._repository = repository

    async def get_by_user(self, query: GetByUserQuery) -> list[ConsumptionRanking]:
        return await self._repository.find_by_user_id(query.user_id)
