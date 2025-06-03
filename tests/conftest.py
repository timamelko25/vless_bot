import asyncio
import sys
import psycopg2
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .run_migrations import run_migrations
import app.database

DB_NAME = "test_db"
DB_USER = "test"
DB_PASSWORD = "test"
DB_HOST = "localhost"
DB_PORT = "5430"


def drop_create_test_db():
    default_conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    default_conn.autocommit = True
    cursor = default_conn.cursor()

    # Drop if exists
    cursor.execute(
        f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{DB_NAME}'"
    )
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    # Create fresh
    cursor.execute(f"CREATE DATABASE {DB_NAME}")
    cursor.close()
    default_conn.close()


@pytest.fixture(scope="session", autouse=True)
def recreate_test_db():
    drop_create_test_db()
    yield
    # Optionally, clean after test run:
    # drop_create_test_db()


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(recreate_test_db):
    run_migrations()


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    # Explicit cleanup
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
    asyncio.set_event_loop(None)  # Clear loop reference


@pytest_asyncio.fixture(scope="module", autouse=True)
async def db_session(apply_migrations):
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5430/test_db",
        echo=False,
        pool_size=50,
        max_overflow=50,
    )

    yield async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(scope="module", autouse=True)
async def override_session(db_session):
    original_session_maker = app.database.async_session_maker

    app.database.async_session_maker = db_session

    yield

    app.database.async_session_maker = original_session_maker
