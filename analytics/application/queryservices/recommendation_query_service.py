"""Query Service for the Recommendation aggregate.

Application layer, read side of the CQRS pattern. Retrieves a user's saving
recommendations without modifying any system state.
"""

from analytics.domain.model.entities.recommendation import Recommendation
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.domain.repositories.recommendation_repository import RecommendationRepository


class RecommendationQueryService:
    """Resolves read queries about recommendations."""

    def __init__(self, repository: RecommendationRepository):
        # Single dependency: the recommendation repository.
        self._repository = repository

    async def get_by_user(self, query: GetByUserQuery) -> list[Recommendation]:
        """Return all recommendations for a user."""
        return await self._repository.find_by_user_id(query.user_id)
