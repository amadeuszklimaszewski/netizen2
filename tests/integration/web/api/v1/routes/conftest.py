from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio

from src.core.models.user import User
from src.core.schemas.jwt import JWTPayload
from src.core.schemas.user import CreateUserSchema
from src.core.services.jwt import encode_jwt
from src.core.services.user import UserService


@pytest.fixture
def create_user_data() -> dict[str, str]:
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
    user = await user_service.create_user(schema)
    user.activate()
    return user


@pytest_asyncio.fixture
async def other_user(
    create_user_data: dict[str, Any],
    user_service: UserService,
) -> User:
    create_user_data["email"] = "other@example.com"
    schema = CreateUserSchema(**create_user_data)
    user = await user_service.create_user(schema)
    user.activate()
    return user


@pytest.fixture
def access_token(user: User) -> str:
    access_token_data = JWTPayload(sub=user.id)
    return encode_jwt(access_token_data)


@pytest.fixture
def user_bearer_token_header(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def other_user_access_token(other_user: User) -> str:
    access_token_data = JWTPayload(sub=other_user.id)
    return encode_jwt(access_token_data)


@pytest.fixture
def other_user_bearer_token_header(other_user_access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {other_user_access_token}"}


@pytest.fixture
def invalid_access_token() -> str:
    access_token_data = JWTPayload(sub=uuid4())
    return encode_jwt(access_token_data)


@pytest.fixture
def invalid_bearer_token_header(invalid_access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {invalid_access_token}"}
