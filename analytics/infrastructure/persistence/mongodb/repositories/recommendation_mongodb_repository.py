from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from analytics.domain.model.entities.recommendation import Recommendation
from analytics.domain.repositories.recommendation_repository import RecommendationRepository
from analytics.infrastructure.persistence.mongodb.model.document_mappers import (
    dataclass_to_document,
    document_to_recommendation,
)
from analytics.infrastructure.persistence.mongodb.repositories.base_mongodb_repository import BaseMongoDBRepository


class RecommendationMongoDBRepository(BaseMongoDBRepository, RecommendationRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "recommendations")

    async def save(self, recommendation: Recommendation) -> Recommendation:
        document = dataclass_to_document(recommendation)
        document = await self._collection.find_one_and_replace(
            {
                "user_id": recommendation.user_id,
                "device_id": recommendation.device_id,
                "recommendation_type": recommendation.recommendation_type,
                "status": "pending",
            },
            document,
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return document_to_recommendation(document)

    async def find_by_user_id(self, user_id: str) -> list[Recommendation]:
        documents = await self._find_by_user_id(user_id)
        return [document_to_recommendation(document) for document in documents]

    async def mark_applied(self, recommendation_id: str) -> Recommendation | None:
        object_id = self._object_id(recommendation_id)
        if object_id is None:
            return None
        document = await self._collection.find_one_and_update(
            {"_id": object_id},
            {"$set": {"status": "applied", "applied_at": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER,
        )
        return document_to_recommendation(document) if document else None
