import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient
from app.main import app
from app.core.config import settings
from app.core.security import get_password_hash, create_access_token

TEST_DB_NAME = "ai_resume_analyzer_test"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[TEST_DB_NAME]
    yield db
    await client.drop_database(TEST_DB_NAME)
    client.close()


@pytest.fixture
async def client(test_db):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def auth_headers(test_db):
    """Create a test user and return Authorization headers."""
    await test_db["users"].delete_many({"email": "test@example.com"})
    user = {
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword123"),
        "full_name": "Test Recruiter",
        "role": "recruiter",
        "is_active": True,
    }
    result = await test_db["users"].insert_one(user)
    token = create_access_token(str(result.inserted_id))
    return {"Authorization": f"Bearer {token}"}
