from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase


class BaseMongoDBRepository:
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str):
        self._collection = database[collection_name]

    def _object_id(self, value: str) -> ObjectId | None:
        try:
            return ObjectId(value)
        except (InvalidId, TypeError):
            return None

    async def _find_by_user_id(self, user_id: str) -> list[dict[str, Any]]:
        cursor = self._collection.find({"user_id": user_id}).sort("created_at", -1)
        return [document async for document in cursor]
