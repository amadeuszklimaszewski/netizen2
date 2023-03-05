from datetime import datetime, timedelta

import pytest

from src.core.exceptions import (
    AlreadyActiveError,
    ExpiredTokenError,
    InvalidTokenError,
    UserNotActiveError,
)
from src.core.models.user import User
from src.core.utils import verify_password


@pytest.fixture
def user():
    return User(
        email="test@example.com",
        password_hash="password_hash",
    )


@pytest.fixture
def active_user(user: User):
    user.activate()
    return user


def test_generate_email_confirmation_token(user: User):
    token = user.generate_email_confirmation_token()

    assert token is not None


def test_generate_password_reset_token(user: User):
    token = user.generate_password_reset_token()

    assert token is not None
    assert user.password_reset_token_expires_at is not None


def test_activate(user: User):
    user.activate()

    assert user.is_active


def test_activate_already_active(active_user: User):
    with pytest.raises(AlreadyActiveError):
        active_user.activate()


def test_confirm_email(user: User):
    token = user.generate_email_confirmation_token()

    user.confirm_email(token)

    assert user.is_active
    assert user.email_confirmation_token is None


def test_confirm_email_invalid_token(user: User):
    token = user.generate_email_confirmation_token()

    # generate new token and invalidate the old one
    user.generate_email_confirmation_token()

    with pytest.raises(InvalidTokenError):
        user.confirm_email(token)

    with pytest.raises(InvalidTokenError):
        user.confirm_email("some_invalid_token")


def test_deactivate(active_user: User):
    active_user.deactivate()

    assert not active_user.is_active


def test_deactivate_already_inactive(user: User):
    with pytest.raises(UserNotActiveError):
        user.deactivate()


def test_reset_password(user: User):
    token = user.generate_password_reset_token()

    user.reset_password(token, "new_password")

    assert verify_password("new_password", user.password_hash)
    assert user.password_reset_token is None
    assert user.password_reset_token_expires_at is None


def test_reset_password_invalid_token(user: User):
    token = user.generate_password_reset_token()

    # generate new token and invalidate the old one
    user.generate_password_reset_token()

    with pytest.raises(InvalidTokenError):
        user.reset_password(token, "new_password")

    with pytest.raises(InvalidTokenError):
        user.reset_password("some_invalid_token", "new_password")


def test_reset_password_expired_token(user: User):
    token = user.generate_password_reset_token()
    user.password_reset_token_expires_at = datetime.now() - timedelta(hours=1)

    with pytest.raises(ExpiredTokenError):
        user.reset_password(token, "new_password")


def test_get_email_context(user: User):
    context = user.get_email_context()

    assert context == {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "email_confirmation_token": user.email_confirmation_token,
        "password_reset_token": user.password_reset_token,
    }
