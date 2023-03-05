from uuid import uuid4

import pytest
import pytest_asyncio
from pytest_mock import MockerFixture

from src.core.exceptions import (
    AlreadyActiveError,
    AlreadyExistsError,
    DoesNotExistError,
    InvalidTokenError,
)
from src.core.models.user import User
from src.core.schemas.email import EmailSchema
from src.core.schemas.user import CreateUserSchema
from src.core.services.user import UserService


@pytest.fixture
def create_user_schema() -> CreateUserSchema:
    return CreateUserSchema(
        email="test@example.com",
        password="password",
        repeat_password="password",
    )


@pytest_asyncio.fixture
async def user(create_user_schema: CreateUserSchema, user_service: UserService) -> User:
    return await user_service.create_user(create_user_schema)


@pytest.mark.asyncio
async def test_create_user(
    create_user_schema: CreateUserSchema,
    user_service: UserService,
) -> None:
    user = await user_service.create_user(create_user_schema)

    assert user is not None
    assert user.email == "test@example.com"
    assert user.password_hash is not None
    assert not user.is_active


@pytest.mark.asyncio
async def test_create_user_already_exists(
    create_user_schema: CreateUserSchema,
    user_service: UserService,
    user: User,
) -> None:
    with pytest.raises(AlreadyExistsError):
        await user_service.create_user(create_user_schema)


@pytest.mark.asyncio
async def test_get_user(user_service: UserService, user: User) -> None:
    user = await user_service.get_user(user.id)

    assert user is not None
    assert user.email == "test@example.com"
    assert user.password_hash is not None
    assert not user.is_active


@pytest.mark.asyncio
async def test_get_user_does_not_exist(user_service: UserService) -> None:
    with pytest.raises(DoesNotExistError):
        await user_service.get_user(uuid4())


@pytest.mark.asyncio
async def test_get_users(user_service: UserService, user: User) -> None:
    users = await user_service.get_users()

    assert users == [user]


@pytest.mark.asyncio
async def test_activate_user(user_service: UserService, user: User) -> None:
    await user_service.activate_user(user.id)

    user = await user_service.get_user(user.id)

    assert user.is_active


@pytest.mark.asyncio
async def test_send_activation_email(
    user_service: UserService,
    user: User,
    mocker: MockerFixture,
) -> None:
    user_service.email_service.send_email = mocker.Mock()  # type: ignore

    await user_service.send_activation_email(user.id)

    assert user.email_confirmation_token is not None

    expected_email = EmailSchema(
        subject="Thank you for registering - activate your account",
        recipients=(user.email,),
        template_name="user_activation.html",
        context=user.get_email_context(),
    )
    assert user_service.email_service.send_email.mock_calls == [  # type: ignore
        mocker.call(expected_email),
    ]


@pytest.mark.asyncio
async def test_send_activation_email_does_not_exist(user_service: UserService) -> None:
    with pytest.raises(DoesNotExistError):
        await user_service.send_activation_email(uuid4())


@pytest.mark.asyncio
async def test_send_activation_email_already_active(
    user_service: UserService,
    user: User,
) -> None:
    user.activate()

    with pytest.raises(AlreadyActiveError):
        await user_service.send_activation_email(user.id)


@pytest.mark.asyncio
async def test_confirm_email(user_service: UserService, user: User) -> None:
    token = user.generate_email_confirmation_token()
    await user_service.confirm_email(user.id, token)

    user = await user_service.get_user(user.id)

    assert user.is_active
    assert user.email_confirmation_token is None


@pytest.mark.asyncio
async def test_confirm_email_does_not_exist(user_service: UserService) -> None:
    token = uuid4().hex
    with pytest.raises(DoesNotExistError):
        await user_service.confirm_email(uuid4(), token)


@pytest.mark.asyncio
async def test_confirm_email_invalid_token(
    user_service: UserService,
    user: User,
) -> None:
    token = uuid4().hex
    user.generate_email_confirmation_token()

    with pytest.raises(InvalidTokenError):
        await user_service.confirm_email(user.id, token)

    user = await user_service.get_user(user.id)

    assert not user.is_active
    assert user.email_confirmation_token is not None


@pytest.mark.asyncio
async def test_send_password_reset_email(
    user_service: UserService,
    user: User,
    mocker: MockerFixture,
) -> None:
    user_service.email_service.send_email = mocker.Mock()  # type: ignore
    await user_service.send_password_reset_email(user.email)

    assert user.password_reset_token is not None

    expected_email = EmailSchema(
        subject="Password reset",
        recipients=(user.email,),
        template_name="password_reset.html",
        context=user.get_email_context(),
    )
    assert user_service.email_service.send_email.mock_calls == [  # type: ignore
        mocker.call(expected_email),
    ]


@pytest.mark.asyncio
async def test_send_password_reset_email_does_not_exist(
    user_service: UserService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await user_service.send_password_reset_email("invalid@example.com")


@pytest.mark.asyncio
async def test_reset_password(user_service: UserService, user: User) -> None:
    token = user.generate_password_reset_token()
    await user_service.reset_password(user.id, token, "new_password")

    user = await user_service.get_user(user.id)

    assert user.password_reset_token is None
    assert user.password_hash is not None


@pytest.mark.asyncio
async def test_reset_password_does_not_exist(user_service: UserService) -> None:
    token = uuid4().hex

    with pytest.raises(DoesNotExistError):
        await user_service.reset_password(uuid4(), token, "new_password")


@pytest.mark.asyncio
async def test_reset_password_invalid_token(
    user_service: UserService,
    user: User,
) -> None:
    token = uuid4().hex
    user.generate_password_reset_token()

    with pytest.raises(InvalidTokenError):
        await user_service.reset_password(user.id, token, "new_password")

    user = await user_service.get_user(user.id)

    assert user.password_reset_token is not None
    assert user.password_hash is not None
