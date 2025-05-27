from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.exc import SQLAlchemyError

from src.core.settings import settings
from src.db.base import Base
from src.services.logger_service import logger


DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


# Dependency injection para FastAPI
async def get_db_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# DEPRECATED BUT USEFUL
async def create_database():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database and tables created successfully.")
    except SQLAlchemyError as e:
        logger.error(f"❌ Error creating database: {e}")
        raise


async def drop_database():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("⚠️  Database dropped successfully.")
    except SQLAlchemyError as e:
        logger.error(f"❌ Error dropping database: {e}")
        raise


def run_migrations_sync():
    logger.info("🚧 Running migrations...")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "src/migrations")

    try:
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ Migrations applied successfully.")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise e

    logger.info("✅ Alembic migrations applied successfully.")
