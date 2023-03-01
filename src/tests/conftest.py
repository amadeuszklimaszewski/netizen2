from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from src.infrastructure.database.metadata import metadata
from src.infrastructure.database.tables import load_all_tables
from src.settings import Settings
from src.web.application import get_app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def async_db_engine() -> AsyncGenerator[AsyncEngine, None]:
    load_all_tables()

    settings = Settings(TESTING=True)  # type: ignore
    engine = create_async_engine(settings.postgres_url)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def async_db_connection(
    async_db_engine: AsyncEngine,
) -> AsyncGenerator[AsyncConnection, None]:
    async with async_db_engine.begin() as conn:
        yield conn


@pytest.fixture
def fastapi_app() -> FastAPI:
    application = get_app()
    return application  # noqa: WPS331


@pytest_asyncio.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        yield client
