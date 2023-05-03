from datetime import date
from uuid import uuid4

import pytest
import pytest_asyncio

from src.core.exceptions import InvalidCredentialsError, UserNotActiveError
from src.core.models.user import User
from src.core.schemas.auth import UserCredentials
from src.core.schemas.jwt import JWTPayload
from src.core.schemas.user import CreateUserSchema
from src.core.services.auth import AuthService
from src.core.services.jwt import decode_jwt, encode_jwt
from src.core.services.user import UserService


@pytest.fixture
def create_user_schema() -> CreateUserSchema:
    return CreateUserSchema(
        email="test@example.com",
        password="password",
        repeat_password="password",
        date_of_birth=date(1990, 1, 1),
    )


@pytest_asyncio.fixture
async def user(create_user_schema: CreateUserSchema, user_service: UserService) -> User:
    return await user_service.create_user(create_user_schema)


@pytest.mark.asyncio
async def test_create_access_token(user: User, auth_service: AuthService) -> None:
    access_token = auth_service.create_access_token(user)

    payload = decode_jwt(access_token)
    assert payload.sub == user.id


@pytest.mark.asyncio
async def test_verify_access_token(
    user: User,
    auth_service: AuthService,
) -> None:
    user.activate()

    access_token = auth_service.create_access_token(user)
    verified_user = await auth_service.verify_access_token(access_token)

    assert user.id == verified_user.id


@pytest.mark.asyncio
async def test_verify_access_token_with_invalid_token(
    user: User,
    auth_service: AuthService,
) -> None:
    user.activate()

    with pytest.raises(InvalidCredentialsError):
        await auth_service.verify_access_token("invalid_token")


@pytest.mark.asyncio
async def test_verify_access_token_with_inactive_user(
    user: User,
    auth_service: AuthService,
) -> None:
    access_token = auth_service.create_access_token(user)

    with pytest.raises(UserNotActiveError):
        await auth_service.verify_access_token(access_token)


@pytest.mark.asyncio
async def test_verify_access_token_with_invalid_user(
    auth_service: AuthService,
) -> None:
    payload = JWTPayload(sub=uuid4())
    access_token = encode_jwt(payload)

    with pytest.raises(InvalidCredentialsError):
        await auth_service.verify_access_token(access_token)


@pytest.mark.asyncio
async def test_authenticate_user(
    user: User,
    auth_service: AuthService,
) -> None:
    user.activate()

    credentials = UserCredentials(email=user.email, password="password")
    token = await auth_service.authenticate_user(credentials)

    payload = decode_jwt(token.access_token)
    assert payload.sub == user.id


@pytest.mark.asyncio
async def test_authenticate_user_with_invalid_password(
    user: User,
    auth_service: AuthService,
) -> None:
    user.activate()

    credentials = UserCredentials(email=user.email, password="invalid_password")
    with pytest.raises(InvalidCredentialsError):
        await auth_service.authenticate_user(credentials)


@pytest.mark.asyncio
async def test_authenticate_user_with_inactive_user(
    user: User,
    auth_service: AuthService,
) -> None:
    credentials = UserCredentials(email=user.email, password="password")
    with pytest.raises(UserNotActiveError):
        await auth_service.authenticate_user(credentials)


@pytest.mark.asyncio
async def test_authenticate_user_with_invalid_email(
    user: User,
    auth_service: AuthService,
) -> None:
    user.activate()

    credentials = UserCredentials(email="invalid@example.com", password="password")
    with pytest.raises(InvalidCredentialsError):
        await auth_service.authenticate_user(credentials)


@pytest.mark.asyncio
async def test_authenticate_user_with_invalid_email_and_password(
    user: User,
    auth_service: AuthService,
) -> None:
    user.activate()

    credentials = UserCredentials(
        email="invalid@example.com",
        password="invalid_password",
    )
    with pytest.raises(InvalidCredentialsError):
        await auth_service.authenticate_user(credentials)
