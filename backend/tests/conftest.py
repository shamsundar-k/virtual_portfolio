"""
Test configuration.

Uses a real MongoDB test database (stock_tracker_test) — no mocks.
A fresh Motor client is created per test to avoid event-loop binding issues.
All test collections are dropped before each test for a clean slate.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

import db as db_module
from config import MONGODB_URI
from main import app

TEST_DB = "stock_tracker_test"
COLLECTIONS = ["portfolios", "trades", "alerts", "journal", "stock_cache"]


@pytest_asyncio.fixture(autouse=True)
async def setup_and_clean_db():
    """Create a fresh Motor client per test and wipe collections."""
    db_module.client = AsyncIOMotorClient(MONGODB_URI)
    db_module.DB_NAME = TEST_DB

    test_db = db_module.client[TEST_DB]
    for col in COLLECTIONS:
        await test_db[col].drop()

    yield

    db_module.client.close()


@pytest_asyncio.fixture
async def client():
    """HTTP client that talks to the app without triggering the lifespan."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def portfolio(client):
    """Create a single portfolio and return the response JSON."""
    resp = await client.post(
        "/portfolios", json={"name": "Test Portfolio", "starting_amount": 100000}
    )
    assert resp.status_code == 201
    return resp.json()
