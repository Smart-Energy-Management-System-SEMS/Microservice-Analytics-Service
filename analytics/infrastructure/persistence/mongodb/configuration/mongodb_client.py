from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from analytics.infrastructure.configuration.settings import Settings


class MongoDBClient:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client: AsyncIOMotorClient | None = None

    async def connect(self) -> None:
        self._client = AsyncIOMotorClient(self._settings.mongodb_uri)
        await self._client.admin.command("ping")

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()

    @property
    def database(self) -> AsyncIOMotorDatabase:
        if self._client is None:
            raise RuntimeError("MongoDB client is not connected")
        return self._client[self._settings.mongodb_database]
