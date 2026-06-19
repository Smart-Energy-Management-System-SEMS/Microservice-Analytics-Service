"""Query Service for the BillPrediction aggregate.

Application layer, read side of the CQRS pattern. Retrieves bill predictions
without modifying any system state.
"""

from analytics.domain.model.entities.bill_prediction import BillPrediction
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.domain.repositories.bill_prediction_repository import BillPredictionRepository


class BillPredictionQueryService:
    """Resolves read queries about bill predictions."""

    def __init__(self, repository: BillPredictionRepository):
        # Single dependency: the bill prediction repository.
        self._repository = repository

    async def get_by_user(self, query: GetByUserQuery) -> list[BillPrediction]:
        """Return all bill predictions for a user."""
        return await self._repository.find_by_user_id(query.user_id)
