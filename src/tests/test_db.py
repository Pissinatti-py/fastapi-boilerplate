import asyncpg
import os
import subprocess
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from src.core.settings import settings
from src.services.logger_service import logger


DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
TEST_DB_NAME = f"{settings.POSTGRES_DB}_test"
DEFAULT_DB = "postgres"

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"
)
DATABASE_URL_NO_DB = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DEFAULT_DB}"
)


engine_test = create_async_engine(DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_database_if_not_exists():
    """
    Creates the test database if it does not already exist.
    """
    logger.info(f"🗄️ Checking if test database '{TEST_DB_NAME}' exists...")
    conn = await asyncpg.connect(DATABASE_URL_NO_DB)
    exists = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = $1", TEST_DB_NAME
    )
    if not exists:
        await conn.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
        logger.info(f"✅ Database '{TEST_DB_NAME}' created.")
    else:
        logger.info(f"ℹ️ Database '{TEST_DB_NAME}' already exists.")
    await conn.close()


def run_migrations():
    """
    Runs Alembic migrations on the test database.
    """
    logger.info("🚀 Running migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error(f"❌ Alembic migration error:\n{result.stderr}")
        raise Exception("Alembic migrations failed")
    logger.info(f"✅ Migrations applied successfully:\n{result.stdout}")


async def setup_test_database():
    """
    Prepares the test database:
    - Creates it if it does not exist.
    - Runs all migrations.
    """
    await create_database_if_not_exists()
    run_migrations()
