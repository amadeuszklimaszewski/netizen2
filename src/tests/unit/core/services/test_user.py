from uuid import uuid4

import pytest
import pytest_asyncio
from pytest_mock import MockerFixture

from src.core.exceptions import AlreadyExistsError, DoesNotExistError, InvalidTokenError
from src.core.interfaces.email import EmailService
from src.core.interfaces.repositories.user import UserRepository
from src.core.models.user import User
from src.core.schemas.email import EmailSchema
from src.core.services.user import UserService
from src.tests.fakes.email import FakeEmailService
from src.tests.fakes.repositories.user import FakeUserRepository


@pytest.fixture
def user_repository() -> UserRepository:
    return FakeUserRepository()


@pytest.fixture
def email_service() -> EmailService:
    return FakeEmailService()


@pytest.fixture
def user_service(
    user_repository: UserRepository,
    email_service: EmailService,
) -> UserService:
    return UserService(user_repository, email_service)


@pytest_asyncio.fixture
async def user(user_service: UserService) -> User:
    user_data = {
        "email": "test@example.com",
        "password": "password",
    }
    return await user_service.create_user(user_data)


@pytest.mark.asyncio
async def test_create_user(user_service: UserService) -> None:
    user_data = {
        "email": "test@example.com",
        "password": "password",
    }
    user = await user_service.create_user(user_data)

    assert user is not None
    assert user.email == "test@example.com"
    assert user.password_hash is not None
    assert not user.is_active


@pytest.mark.asyncio
async def test_create_user_already_exists(
    user_service: UserService,
    user: User,
) -> None:
    user_data = {
        "email": user.email,
        "password": "password",
    }

    with pytest.raises(AlreadyExistsError):
        await user_service.create_user(user_data)


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
    await user_service.send_password_reset_email(user.id)

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
        await user_service.send_password_reset_email(uuid4())


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
