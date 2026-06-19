"""Query Service for the ConsumptionRanking aggregate.

Application layer, read side of the CQRS pattern. Retrieves previously
generated consumption rankings without altering any system state.
"""

from analytics.domain.model.entities.consumption_ranking import ConsumptionRanking
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.domain.repositories.consumption_ranking_repository import ConsumptionRankingRepository


class ConsumptionRankingQueryService:
    """Resolves read queries about consumption rankings."""

    def __init__(self, repository: ConsumptionRankingRepository):
        # Single dependency: the consumption ranking repository.
        self._repository = repository

    async def get_by_user(self, query: GetByUserQuery) -> list[ConsumptionRanking]:
        """Return all consumption rankings for a user."""
        return await self._repository.find_by_user_id(query.user_id)
