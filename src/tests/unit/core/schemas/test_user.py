import pytest
from pydantic import ValidationError
from src.core.schemas.user import CreateUserSchema


def test_create_user_schema_not_matching_password() -> None:
    with pytest.raises(ValidationError):
        CreateUserSchema(
            email="test@example.com",
            password="password",
            repeat_password="other_password",
        )


def test_create_user_schema_invalid_email() -> None:
    with pytest.raises(ValidationError):
        CreateUserSchema(
            email="invalid_email",
            password="password",
            repeat_password="password",
        )


def test_create_user_schema_too_short_password() -> None:
    with pytest.raises(ValidationError):
        CreateUserSchema(
            email="test@example.com",
            password="pass",
            repeat_password="pass",
        )
