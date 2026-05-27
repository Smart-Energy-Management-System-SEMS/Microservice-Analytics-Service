from motor.motor_asyncio import AsyncIOMotorDatabase

from analytics.domain.model.entities.device_identification_result import DeviceIdentificationResult
from analytics.domain.repositories.device_identification_result_repository import DeviceIdentificationResultRepository
from analytics.infrastructure.persistence.mongodb.model.document_mappers import (
    dataclass_to_document,
    document_to_device_identification,
)
from analytics.infrastructure.persistence.mongodb.repositories.base_mongodb_repository import BaseMongoDBRepository


class DeviceIdentificationResultMongoDBRepository(BaseMongoDBRepository, DeviceIdentificationResultRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "device_identification_results")

    async def save(self, result: DeviceIdentificationResult) -> DeviceIdentificationResult:
        document = dataclass_to_document(result)
        insert_result = await self._collection.insert_one(document)
        document["_id"] = insert_result.inserted_id
        return document_to_device_identification(document)

    async def find_by_user_id(self, user_id: str) -> list[DeviceIdentificationResult]:
        documents = await self._find_by_user_id(user_id)
        return [document_to_device_identification(document) for document in documents]
