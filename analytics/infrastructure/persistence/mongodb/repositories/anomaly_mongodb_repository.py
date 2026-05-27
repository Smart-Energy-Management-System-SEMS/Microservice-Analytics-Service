from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from analytics.domain.model.entities.anomaly import Anomaly
from analytics.domain.repositories.anomaly_repository import AnomalyRepository
from analytics.infrastructure.persistence.mongodb.model.document_mappers import dataclass_to_document, document_to_anomaly
from analytics.infrastructure.persistence.mongodb.repositories.base_mongodb_repository import BaseMongoDBRepository


class AnomalyMongoDBRepository(BaseMongoDBRepository, AnomalyRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "anomalies")

    async def save(self, anomaly: Anomaly) -> Anomaly:
        document = dataclass_to_document(anomaly)
        insert_result = await self._collection.insert_one(document)
        document["_id"] = insert_result.inserted_id
        return document_to_anomaly(document)

    async def find_by_user_id(self, user_id: str) -> list[Anomaly]:
        documents = await self._find_by_user_id(user_id)
        return [document_to_anomaly(document) for document in documents]

    async def mark_resolved(self, anomaly_id: str) -> Anomaly | None:
        object_id = self._object_id(anomaly_id)
        if object_id is None:
            return None
        document = await self._collection.find_one_and_update(
            {"_id": object_id},
            {"$set": {"status": "resolved", "resolved_at": datetime.utcnow()}},
            return_document=True,
        )
        return document_to_anomaly(document) if document else None
