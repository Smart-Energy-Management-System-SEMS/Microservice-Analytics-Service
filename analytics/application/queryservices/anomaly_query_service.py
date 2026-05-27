from analytics.domain.model.entities.anomaly import Anomaly
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.domain.repositories.anomaly_repository import AnomalyRepository


class AnomalyQueryService:
    def __init__(self, repository: AnomalyRepository):
        self._repository = repository

    async def get_by_user(self, query: GetByUserQuery) -> list[Anomaly]:
        return await self._repository.find_by_user_id(query.user_id)
