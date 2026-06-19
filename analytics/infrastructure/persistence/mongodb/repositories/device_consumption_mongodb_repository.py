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
        pipeline = [
            {
                "$match": {
                    "device_id": device_id,
                    "$or": [{"user_id": user_id}, {"owner_id": user_id}],
                }
            },
            {
                "$addFields": {
                    "_normalized_measured_at": {
                        "$ifNull": [
                            "$measured_at",
                            {"$ifNull": ["$measuredAt", {"$ifNull": ["$timestamp", "$occurred_at"]}]},
                        ]
                    }
                }
            },
            {"$sort": {"_normalized_measured_at": -1}},
            {"$limit": limit},
        ]
        documents = [document async for document in self._collection.aggregate(pipeline)]
        return [document_to_device_consumption(document) for document in documents]

    async def summarize_devices_for_period(
        self,
        user_id: str,
        period_start,
        period_end,
    ) -> list[DeviceConsumptionSummary]:
        pipeline = [
            {
                "$match": {
                    "$or": [{"user_id": user_id}, {"owner_id": user_id}],
                }
            },
            {
                "$addFields": {
                    "_normalized_measured_at": {
                        "$ifNull": [
                            "$measured_at",
                            {"$ifNull": ["$measuredAt", {"$ifNull": ["$timestamp", "$occurred_at"]}]},
                        ]
                    },
                    "_normalized_energy_kwh": {
                        "$ifNull": [
                            "$energy_kwh",
                            {
                                "$ifNull": [
                                    "$consumption_kwh",
                                    {"$ifNull": ["$consumptionKwh", "$actual_kwh"]},
                                ]
                            },
                        ]
                    },
                }
            },
            {
                "$match": {
                    "_normalized_measured_at": {"$gte": period_start, "$lt": period_end},
                }
            },
            {
                "$group": {
                    "_id": "$device_id",
                    "total_kwh": {"$sum": "$_normalized_energy_kwh"},
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
                    "$or": [{"user_id": user_id}, {"owner_id": user_id}],
                }
            },
            {
                "$addFields": {
                    "_normalized_measured_at": {
                        "$ifNull": [
                            "$measured_at",
                            {"$ifNull": ["$measuredAt", {"$ifNull": ["$timestamp", "$occurred_at"]}]},
                        ]
                    },
                    "_normalized_energy_kwh": {
                        "$ifNull": [
                            "$energy_kwh",
                            {
                                "$ifNull": [
                                    "$consumption_kwh",
                                    {"$ifNull": ["$consumptionKwh", "$actual_kwh"]},
                                ]
                            },
                        ]
                    },
                }
            },
            {
                "$match": {
                    "_normalized_measured_at": {"$gte": period_start, "$lt": period_end},
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$_normalized_measured_at",
                        }
                    },
                    "total_kwh": {"$sum": "$_normalized_energy_kwh"},
                }
            },
            {"$sort": {"_id": 1}},
        ]
        documents = [document async for document in self._collection.aggregate(pipeline)]
        return [round(float(document["total_kwh"]), 2) for document in documents]
