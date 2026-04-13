from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


class Database:
    client: AsyncIOMotorClient | None = None


db = Database()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def connect_to_mongo() -> None:
    db.client = AsyncIOMotorClient(settings.mongodb_uri)


async def close_mongo_connection() -> None:
    if db.client:
        db.client.close()


def get_database():
    if db.client is None:
        raise RuntimeError("MongoDB client is not initialized")
    return db.client[settings.mongodb_db]
