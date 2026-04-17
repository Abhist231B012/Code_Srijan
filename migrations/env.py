import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from dotenv import load_dotenv

# ── Load .env ──────────────────────────────────────────────────────────────────
load_dotenv()

# ── Alembic Config ─────────────────────────────────────────────────────────────
config = context.config

# Override sqlalchemy.url from environment variable so we never hardcode creds
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/credit_scoring_db")
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# ── Logging ────────────────────────────────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import your models here so Alembic can detect schema changes ───────────────
# Example:
#   from app.db.base import Base
#   from app.db.models.applicant import Applicant
#   from app.db.models.prediction import Prediction
#   target_metadata = Base.metadata
#
# For now we use None — replace once you create your ORM models
target_metadata = None


# ── Offline migrations (generates SQL script without DB connection) ────────────
def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Useful for generating a SQL file to review before applying.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,           # detect column type changes
        compare_server_default=True, # detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


# ── Online migrations (connects to DB and applies directly) ───────────────────
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Create an async engine and run migrations using it.
    This is required because we use asyncpg (async PostgreSQL driver).
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # no connection pooling during migrations
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migrations — runs the async function."""
    asyncio.run(run_async_migrations())


# ── Run ────────────────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()