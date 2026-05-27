from analytics.domain.model.entities.bill_prediction import BillPrediction
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.domain.repositories.bill_prediction_repository import BillPredictionRepository


class BillPredictionQueryService:
    def __init__(self, repository: BillPredictionRepository):
        self._repository = repository

    async def get_by_user(self, query: GetByUserQuery) -> list[BillPrediction]:
        return await self._repository.find_by_user_id(query.user_id)
