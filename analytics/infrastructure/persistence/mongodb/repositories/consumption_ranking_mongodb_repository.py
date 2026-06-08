from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

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
        document = await self._collection.find_one_and_replace(
            {
                "user_id": ranking.user_id,
                "period_type": ranking.period_type,
                "period_start": ranking.period_start,
                "period_end": ranking.period_end,
            },
            document,
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return document_to_consumption_ranking(document)

    async def find_by_user_id(self, user_id: str) -> list[ConsumptionRanking]:
        documents = await self._find_by_user_id(user_id)
        return [document_to_consumption_ranking(document) for document in documents]
