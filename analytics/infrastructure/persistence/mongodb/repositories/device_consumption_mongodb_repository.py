from motor.motor_asyncio import AsyncIOMotorDatabase

from analytics.domain.model.entities.device_consumption import DeviceConsumption
from analytics.domain.repositories.device_consumption_repository import (
    DeviceConsumptionRepository,
    DeviceConsumptionSummary,
)
from analytics.infrastructure.persistence.mongodb.model.document_mappers import (
    dataclass_to_document,
    document_to_device_consumption,
)
from analytics.infrastructure.persistence.mongodb.repositories.base_mongodb_repository import BaseMongoDBRepository


class DeviceConsumptionMongoDBRepository(BaseMongoDBRepository, DeviceConsumptionRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "device_consumptions")

    async def save(self, reading: DeviceConsumption) -> DeviceConsumption:
        document = dataclass_to_document(reading)
        insert_result = await self._collection.insert_one(document)
        document["_id"] = insert_result.inserted_id
        return document_to_device_consumption(document)

    async def find_recent_by_device(
        self,
        user_id: str,
        device_id: str,
        limit: int,
    ) -> list[DeviceConsumption]:
        cursor = (
            self._collection.find({"user_id": user_id, "device_id": device_id})
            .sort("measured_at", -1)
            .limit(limit)
        )
        return [document_to_device_consumption(document) async for document in cursor]

    async def summarize_devices_for_period(
        self,
        user_id: str,
        period_start,
        period_end,
    ) -> list[DeviceConsumptionSummary]:
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "measured_at": {"$gte": period_start, "$lt": period_end},
                }
            },
            {
                "$group": {
                    "_id": "$device_id",
                    "total_kwh": {"$sum": "$energy_kwh"},
                }
            },
            {"$sort": {"total_kwh": -1, "_id": 1}},
        ]
        documents = [document async for document in self._collection.aggregate(pipeline)]
        return [
            DeviceConsumptionSummary(
                device_id=document["_id"],
                total_kwh=round(float(document["total_kwh"]), 2),
                device_name=document["_id"],
            )
            for document in documents
        ]

    async def find_daily_user_totals_for_period(
        self,
        user_id: str,
        period_start,
        period_end,
    ) -> list[float]:
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "measured_at": {"$gte": period_start, "$lt": period_end},
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$measured_at",
                        }
                    },
                    "total_kwh": {"$sum": "$energy_kwh"},
                }
            },
            {"$sort": {"_id": 1}},
        ]
        documents = [document async for document in self._collection.aggregate(pipeline)]
        return [round(float(document["total_kwh"]), 2) for document in documents]
