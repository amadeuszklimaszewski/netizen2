import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient, Response

from src.core.models.user import User
from src.core.schemas.user import CreateUserSchema
from src.core.services.user import UserService


@pytest.fixture
def create_user_data() -> dict[str, str]:
    return {
        "email": "user@example.com",
        "password": "password123",
        "repeat_password": "password123",
        "date_of_birth": "1990-01-01",
    }


@pytest.fixture
def login_data(create_user_data: dict[str, str]) -> dict[str, str]:
    return {
        "username": create_user_data["email"],
        "password": create_user_data["password"],
    }


@pytest_asyncio.fixture
async def user(
    create_user_data: dict[str, str],
    user_service: UserService,
) -> User:
    schema = CreateUserSchema(**create_user_data)  # type: ignore
    user = await user_service.create_user(schema)
    user.activate()
    return user


@pytest.mark.asycnio
async def test_authenticate_user(
    client: AsyncClient,
    user: User,
    login_data: dict[str, str],
):
    response: Response = await client.post("/auth/login/", data=login_data)

    assert response.status_code == status.HTTP_200_OK
