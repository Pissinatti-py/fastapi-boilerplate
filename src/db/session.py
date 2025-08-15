from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import AsyncGenerator

from src.core.settings import settings
from src.db.base import Base
from src.services.logger_service import logger


DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


# Dependency injection para FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# DEPRECATED BUT USEFUL
async def create_database():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except SQLAlchemyError as db_error:
        logger.error(f"❌ Error creating database: {db_error}")
        raise

    logger.info("✅ Database and tables created successfully.")


async def drop_database():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    except SQLAlchemyError as db_error:
        logger.error(f"❌ Error dropping database: {db_error}")
        raise

    logger.info("⚠️  Database dropped successfully.")


def _get_alembic_config():
    """Get configured Alembic config."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "src/migrations")
    return alembic_cfg


def _get_current_db_revision(sync_engine):
    """Get current database revision."""
    with sync_engine.connect() as connection:
        try:
            query_result = connection.execute(
                text("SELECT version_num FROM alembic_version LIMIT 1")
            )
        except Exception:
            # Table doesn't exist, database is not initialized
            return None

        return query_result.scalar()


def _create_sync_engine():
    """Create synchronous engine for migration checks."""
    sync_database_url = DATABASE_URL.replace("+asyncpg", "")
    return create_engine(sync_database_url)


def _get_head_revision():
    """Get the head revision from Alembic script."""
    alembic_cfg = _get_alembic_config()
    script = ScriptDirectory.from_config(alembic_cfg)
    return script.get_current_head()


def check_migration_status():
    """
    Check if migrations are up to date.

    Returns:
        tuple: (needs_migration, current_revision, head_revision)
    """
    try:
        sync_engine = _create_sync_engine()
    except Exception as migration_error:
        logger.warning(f"⚠️ Could not check migration status: {migration_error}")
        return True, None, None

    try:
        head_revision = _get_head_revision()
    except Exception as migration_error:
        logger.warning(f"⚠️ Could not check migration status: {migration_error}")
        return True, None, None

    try:
        current_revision = _get_current_db_revision(sync_engine)
    except Exception as migration_error:
        logger.warning(f"⚠️ Could not check migration status: {migration_error}")
        return True, None, None
    finally:
        sync_engine.dispose()

    needs_migration = current_revision != head_revision
    return needs_migration, current_revision, head_revision


def _log_migration_status(current_revision, head_revision):
    """Log appropriate migration status message."""
    if current_revision is None:
        logger.info("🆕 Database is uninitialized. Running initial migrations...")
    else:
        logger.info(
            f"🔄 Database needs update from {current_revision} to {head_revision}"
        )


def _execute_migration():
    """Execute Alembic migration."""
    logger.info("🚧 Running migrations...")
    alembic_cfg = _get_alembic_config()
    command.upgrade(alembic_cfg, "head")
    logger.info("✅ Migrations applied successfully.")


def _verify_migration(head_revision):
    """Verify migration was successful."""
    migration_needed, current_after, head_after = check_migration_status()

    if not migration_needed:
        logger.info(f"✅ Database successfully updated to revision: {head_after}")
        return

    logger.warning(
        f"⚠️ Migration may not have completed successfully. "
        f"Current: {current_after}, Expected: {head_after}"
    )


def _perform_migration_process(migration_needed, current_revision, head_revision):
    """Perform the complete migration process."""
    if not migration_needed:
        logger.info("✅ Database is already up to date. No migrations needed.")
        return

    _log_migration_status(current_revision, head_revision)
    _execute_migration()
    _verify_migration(head_revision)


def run_migrations_sync():
    """
    Run Alembic migrations synchronously.

    :raises migration_error: If migration fails, re-raises the
        exception to prevent application startup.
    """
    logger.info("🔍 Checking migration status...")

    try:
        migration_needed, current_revision, head_revision = check_migration_status()
    except Exception as migration_error:
        logger.error(f"❌ Migration failed: {migration_error}")
        raise migration_error

    try:
        _perform_migration_process(migration_needed, current_revision, head_revision)
    except Exception as migration_error:
        logger.error(f"❌ Migration failed: {migration_error}")
        raise migration_error
