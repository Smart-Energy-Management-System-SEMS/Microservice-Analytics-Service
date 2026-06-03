"""Query Service for DeviceIdentificationResult.

Application layer, read side of the CQRS pattern. Retrieves device
identification results without modifying any state.
"""

from analytics.domain.model.entities.device_identification_result import DeviceIdentificationResult
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.domain.repositories.device_identification_result_repository import DeviceIdentificationResultRepository


class DeviceIdentificationQueryService:
    """Resolves read queries about device identifications."""

    def __init__(self, repository: DeviceIdentificationResultRepository):
        # Single dependency: the device identification result repository.
        self._repository = repository

    async def get_by_user(self, query: GetByUserQuery) -> list[DeviceIdentificationResult]:
        """Return all device identifications for a user."""
        return await self._repository.find_by_user_id(query.user_id)
