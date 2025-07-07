import os

from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

import asyncio

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.app_config import app_settings
from app.db.session import Base
from app.main import app

# Use your actual test DB URL here!
TEST_DATABASE_URL = app_settings.database_url


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def engine():
    # Create the test engine and tables ONCE per session
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(engine):
    """
    For each test, open a transaction and roll back at the end.
    """
    async with engine.connect() as conn:
        # Begin a new transaction for this test
        transaction = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()  # Rollback all changes made during the test


@pytest.fixture(scope="function")
async def client(db_session, monkeypatch):
    """
    Override get_db to use the transactional session for each test.
    """
    from app.db.session import get_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    # with TestClient(app) as c:
    #     yield c
    from httpx import ASGITransport

    async with AsyncClient(
        base_url="http://test", transport=ASGITransport(app=app)
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
