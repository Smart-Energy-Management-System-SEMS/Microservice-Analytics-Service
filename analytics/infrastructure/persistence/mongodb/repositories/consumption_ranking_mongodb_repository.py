from motor.motor_asyncio import AsyncIOMotorDatabase

from analytics.domain.model.entities.consumption_ranking import ConsumptionRanking
from analytics.domain.repositories.consumption_ranking_repository import ConsumptionRankingRepository
from analytics.infrastructure.persistence.mongodb.model.document_mappers import (
    dataclass_to_document,
    document_to_consumption_ranking,
)
from analytics.infrastructure.persistence.mongodb.repositories.base_mongodb_repository import BaseMongoDBRepository


class ConsumptionRankingMongoDBRepository(BaseMongoDBRepository, ConsumptionRankingRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "consumption_rankings")

    async def save(self, ranking: ConsumptionRanking) -> ConsumptionRanking:
        document = dataclass_to_document(ranking)
        insert_result = await self._collection.insert_one(document)
        document["_id"] = insert_result.inserted_id
        return document_to_consumption_ranking(document)

    async def find_by_user_id(self, user_id: str) -> list[ConsumptionRanking]:
        documents = await self._find_by_user_id(user_id)
        return [document_to_consumption_ranking(document) for document in documents]
