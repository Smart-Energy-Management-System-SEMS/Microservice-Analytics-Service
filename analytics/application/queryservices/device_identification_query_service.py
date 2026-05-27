from analytics.domain.model.entities.device_identification_result import DeviceIdentificationResult
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.domain.repositories.device_identification_result_repository import DeviceIdentificationResultRepository


class DeviceIdentificationQueryService:
    def __init__(self, repository: DeviceIdentificationResultRepository):
        self._repository = repository

    async def get_by_user(self, query: GetByUserQuery) -> list[DeviceIdentificationResult]:
        return await self._repository.find_by_user_id(query.user_id)
