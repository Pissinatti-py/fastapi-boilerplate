import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from src.main import app
from src.db.session import get_db_session
from src.tests.test_db import (
    TestSessionLocal,
    setup_test_database,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    """
    This fixture runs once per test session to initialize
    the database schema before any tests are executed.

    :return: None
    :rtype: None
    """
    await setup_test_database()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_session() -> AsyncSession:
    """
    This fixture creates a new database session for each test session,
    ensuring isolation between tests.

    :return: SQLAlchemy asynchronous session
    :rtype: AsyncSession
    :yield: AsyncSession instance for database interaction during the test
    """
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def client(db_session: AsyncSession):
    """
    This fixture creates a `TestClient` that overrides the default database
    session with the test session for isolated integration testing.

    :param db_session: Async SQLAlchemy session used for the test.
    :type db_session: AsyncSession
    :yield: FastAPI test client with database dependency overridden.
    :rtype: TestClient
    """

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
