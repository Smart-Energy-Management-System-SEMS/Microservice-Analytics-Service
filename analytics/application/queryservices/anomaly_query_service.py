"""Query Service for the Anomaly aggregate.

Application layer, the "read" side of the CQRS pattern. Unlike Command
Services, this one does not modify state nor publish events: it only retrieves
data through the repository to answer queries.
"""

from analytics.domain.model.entities.anomaly import Anomaly
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.domain.repositories.anomaly_repository import AnomalyRepository


class AnomalyQueryService:
    """Resolves read queries about anomalies."""

    def __init__(self, repository: AnomalyRepository):
        # Only the repository is needed (no rules or events on the read side).
        self._repository = repository

    async def get_by_user(self, query: GetByUserQuery) -> list[Anomaly]:
        """Return all anomalies associated with a user."""
        return await self._repository.find_by_user_id(query.user_id)
