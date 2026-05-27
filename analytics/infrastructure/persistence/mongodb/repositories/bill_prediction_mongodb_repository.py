from motor.motor_asyncio import AsyncIOMotorDatabase

from analytics.domain.model.entities.bill_prediction import BillPrediction
from analytics.domain.repositories.bill_prediction_repository import BillPredictionRepository
from analytics.infrastructure.persistence.mongodb.model.document_mappers import (
    dataclass_to_document,
    document_to_bill_prediction,
)
from analytics.infrastructure.persistence.mongodb.repositories.base_mongodb_repository import BaseMongoDBRepository


class BillPredictionMongoDBRepository(BaseMongoDBRepository, BillPredictionRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "bill_predictions")

    async def save(self, prediction: BillPrediction) -> BillPrediction:
        document = dataclass_to_document(prediction)
        insert_result = await self._collection.insert_one(document)
        document["_id"] = insert_result.inserted_id
        return document_to_bill_prediction(document)

    async def find_by_user_id(self, user_id: str) -> list[BillPrediction]:
        documents = await self._find_by_user_id(user_id)
        return [document_to_bill_prediction(document) for document in documents]
