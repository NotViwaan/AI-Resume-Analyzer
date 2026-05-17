from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None


async def connect_db() -> None:
    global _client
    _client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=5000,
        maxPoolSize=50,
        minPoolSize=10,
    )
    # Ping to confirm connection
    await _client.admin.command("ping")
    logger.info(f"Connected to MongoDB at {settings.MONGODB_URL}")

    # Create indexes on startup
    db = _client[settings.MONGODB_DB_NAME]
    await _create_indexes(db)


async def disconnect_db() -> None:
    global _client
    if _client:
        _client.close()
        logger.info("Disconnected from MongoDB")


async def get_database() -> AsyncIOMotorDatabase:
    if _client is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _client[settings.MONGODB_DB_NAME]


async def _create_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create all collection indexes for performance."""
    from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT

    # Users
    await db["users"].create_indexes([
        IndexModel([("email", ASCENDING)], unique=True),
        IndexModel([("created_at", DESCENDING)]),
    ])

    # Candidates
    await db["candidates"].create_indexes([
        IndexModel([("email", ASCENDING)], unique=True),
        IndexModel([("created_at", DESCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([
            ("first_name", TEXT),
            ("last_name", TEXT),
            ("email", TEXT),
        ], name="candidate_search"),
    ])

    # Jobs
    await db["jobs"].create_indexes([
        IndexModel([("created_at", DESCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("title", TEXT), ("description", TEXT)], name="job_search"),
    ])

    # Resumes
    await db["resumes"].create_indexes([
        IndexModel([("candidate_id", ASCENDING)]),
        IndexModel([("job_id", ASCENDING)]),
        IndexModel([("created_at", DESCENDING)]),
        IndexModel([("ai_score", DESCENDING)]),
        IndexModel([("candidate_id", ASCENDING), ("job_id", ASCENDING)], unique=True),
    ])

    logger.info("Database indexes created successfully")
