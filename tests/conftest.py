from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine
from tests.fakes.database import FakeDatabase
from tests.fakes.email import FakeEmailSender
from tests.fakes.repositories.group import (
    FakeGroupMemberRepository,
    FakeGroupRepository,
    FakeGroupRequestRepository,
)
from tests.fakes.repositories.user import FakeUserRepository

from src.core.interfaces.email import EmailSender
from src.core.interfaces.repositories.group import (
    GroupMemberRepository,
    GroupRepository,
    GroupRequestRepository,
)
from src.core.interfaces.repositories.user import UserRepository
from src.core.services.auth import AuthService
from src.core.services.group import GroupService
from src.core.services.user import UserService
from src.infrastructure.database.metadata import metadata
from src.infrastructure.database.tables import load_all_tables
from src.settings import Settings
from src.web.api.v1.dependencies import (
    get_email_sender,
    get_group_member_repository,
    get_group_repository,
    get_group_request_repository,
    get_user_repository,
)
from src.web.application import get_app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest_asyncio.fixture
async def async_db_engine() -> AsyncGenerator[AsyncEngine, None]:
    load_all_tables()

    settings = Settings(TESTING=True)  # type: ignore
    engine = create_async_engine(settings.postgres_url)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest_asyncio.fixture
async def async_db_connection(
    async_db_engine: AsyncEngine,
) -> AsyncGenerator[AsyncConnection, None]:
    async with async_db_engine.begin() as conn:
        yield conn
        await conn.rollback()


@pytest.fixture
def fake_db() -> FakeDatabase:
    return FakeDatabase()


@pytest.fixture
def user_repository(fake_db: FakeDatabase) -> UserRepository:
    return FakeUserRepository(fake_db)


@pytest.fixture
def user_service(
    user_repository: UserRepository,
    email_sender: EmailSender,
) -> UserService:
    return UserService(user_repository, email_sender)


@pytest.fixture
def auth_service(
    user_repository: UserRepository,
) -> AuthService:
    return AuthService(user_repository)


@pytest.fixture
def group_repository(fake_db: FakeDatabase) -> GroupRepository:
    return FakeGroupRepository(fake_db)


@pytest.fixture
def group_member_repository(fake_db: FakeDatabase) -> GroupMemberRepository:
    return FakeGroupMemberRepository(fake_db)


@pytest.fixture
def group_request_repository(fake_db: FakeDatabase) -> GroupRequestRepository:
    return FakeGroupRequestRepository(fake_db)


@pytest.fixture
def group_service(
    group_repository: GroupRepository,
    group_member_repository: GroupMemberRepository,
    group_request_repository: GroupRequestRepository,
) -> GroupService:
    return GroupService(
        group_repository,
        group_member_repository,
        group_request_repository,
    )


@pytest.fixture
def email_sender() -> EmailSender:
    return FakeEmailSender()


@pytest.fixture
def fastapi_app(
    email_sender: EmailSender,
    user_repository: UserRepository,
    group_repository: GroupRepository,
    group_member_repository: GroupMemberRepository,
    group_request_repository: GroupRequestRepository,
) -> FastAPI:
    app = get_app()
    app.dependency_overrides[get_user_repository] = lambda: user_repository
    app.dependency_overrides[get_email_sender] = lambda: email_sender
    app.dependency_overrides[get_group_repository] = lambda: group_repository
    app.dependency_overrides[
        get_group_member_repository
    ] = lambda: group_member_repository
    app.dependency_overrides[
        get_group_request_repository
    ] = lambda: group_request_repository

    return app  # noqa: WPS331


@pytest_asyncio.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=fastapi_app, base_url="http://test/api/v1") as client:
        yield client
