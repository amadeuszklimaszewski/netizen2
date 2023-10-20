from datetime import date
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncConnection

from src.core.exceptions import AlreadyExistsError, DoesNotExistError
from src.core.interfaces.email import EmailSender
from src.core.models.user import User
from src.core.schemas.user import CreateUserSchema
from src.core.services.user import UserService
from src.infrastructure.repositories.user import UserRepository


@pytest.fixture
def user_repository(async_db_connection: AsyncConnection) -> UserRepository:
    return UserRepository(async_db_connection)


@pytest.fixture
def user_service(
    user_repository: UserRepository,
    email_sender: EmailSender,
) -> UserService:
    return UserService(user_repository, email_sender)


@pytest.fixture
def create_user_data() -> dict[str, Any]:
    return {
        "email": "user@example.com",
        "password": "password123",
        "repeat_password": "password123",
        "date_of_birth": "1990-01-01",
    }


@pytest_asyncio.fixture
async def user(
    create_user_data: dict[str, Any],
    user_service: UserService,
) -> User:
    schema = CreateUserSchema(**create_user_data)
    return await user_service.create_user(schema)


@pytest.mark.asyncio
async def test_get_by_email(user_repository: UserRepository, user: User):
    result = await user_repository.get_by_email(user.email)
    assert result == user


@pytest.mark.asyncio
async def test_get_user(user_repository: UserRepository, user: User):
    result = await user_repository.get(user.id)
    assert result == user


@pytest.mark.asyncio
async def test_get_user_does_not_exist(user_repository: UserRepository):
    with pytest.raises(DoesNotExistError):
        await user_repository.get(uuid4())


@pytest.mark.asyncio
async def test_get_all_users(user_repository: UserRepository, user: User):
    users = await user_repository.get_many()
    assert users == [user]


@pytest.mark.asyncio
async def test_persist_user(
    create_user_data: dict[str, Any],
    user_repository: UserRepository,
):
    user = User(
        email=create_user_data["email"],
        date_of_birth=create_user_data["date_of_birth"],
        password_hash="test",
    )
    await user_repository.persist(user)
    result = await user_repository.get_by_email(user.email)
    assert result == user


@pytest.mark.asyncio
async def test_persist_user_already_exists(user_repository: UserRepository, user: User):
    with pytest.raises(AlreadyExistsError):
        await user_repository.persist(user)


@pytest.mark.asyncio
async def test_persist_many(user_repository: UserRepository):
    user1 = User(
        email="test1@example.com",
        date_of_birth=date(1990, 1, 1),
        password_hash="test",
    )
    user2 = User(
        email="test2@example.com",
        date_of_birth=date(1990, 1, 1),
        password_hash="test",
    )
    users = [user1, user2]

    await user_repository.persist_many(users)
    result = await user_repository.get_many()

    assert len(result) == 2
    assert user1 in result
    assert user2 in result


@pytest.mark.asyncio
async def test_persist_many_with_already_exists(user_repository: UserRepository):
    user1 = User(
        email="test1@example.com",
        date_of_birth=date(1990, 1, 1),
        password_hash="test",
    )
    user2 = User(
        email="test2@example.com",
        date_of_birth=date(1990, 1, 1),
        password_hash="test",
    )
    users = [user1, user2]
    await user_repository.persist_many(users)

    with pytest.raises(AlreadyExistsError):
        await user_repository.persist_many(users)


@pytest.mark.asyncio
async def test_delete_user(user_repository: UserRepository, user: User):
    await user_repository.delete(user)
    result = await user_repository.get_by_email(user.email)
    assert result is None


@pytest.mark.asyncio
async def test_update_user(user_repository: UserRepository, user: User):
    user.email = "new@example.com"
    await user_repository.update(user, fields_to_update=["email"])
    result = await user_repository.get_by_email(user.email)

    assert result is not None
    assert result.email == user.email
    assert result.first_name == user.first_name


@pytest.mark.asyncio
async def test_update_with_selected_fields(user_repository: UserRepository, user: User):
    user.email = "new@example.com"
    user.first_name = "John"

    await user_repository.update(user, fields_to_update=["email"])
    result = await user_repository.get_by_email(user.email)

    assert result is not None
    assert result.email == user.email
    assert result.first_name is None
