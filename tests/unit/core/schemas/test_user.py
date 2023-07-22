from datetime import date, datetime

import pytest
from pydantic import ValidationError

from src.core.schemas.user import (
    CreateUserSchema,
    DateOfBirthInputSchema,
    UpdateUserSchema,
)
from src.settings import settings


def test_create_user_schema_not_matching_password() -> None:
    with pytest.raises(ValidationError):
        CreateUserSchema(
            email="test@example.com",
            password="password",
            repeat_password="other_password",
            date_of_birth=date(1990, 1, 1),
        )


def test_create_user_schema_invalid_email() -> None:
    with pytest.raises(ValidationError):
        CreateUserSchema(
            email="invalid_email",
            password="password",
            repeat_password="password",
            date_of_birth=date(1990, 1, 1),
        )


def test_create_user_schema_too_short_password() -> None:
    with pytest.raises(ValidationError):
        CreateUserSchema(
            email="test@example.com",
            password="pass",
            repeat_password="pass",
            date_of_birth=date(1990, 1, 1),
        )


def test_date_of_birth_schema_in_future() -> None:
    date_of_birth = date(year=3000, month=1, day=1)
    with pytest.raises(ValidationError):
        DateOfBirthInputSchema(date_of_birth=date_of_birth)


def test_date_of_birth_schema_too_old() -> None:
    date_of_birth = date(year=settings.MINIMUM_YEAR_OF_BIRTH - 1, month=1, day=1)
    with pytest.raises(ValidationError):
        DateOfBirthInputSchema(date_of_birth=date_of_birth)


def test_date_of_birth_schema_too_young() -> None:
    current_year = datetime.now().year
    date_of_birth = date(year=current_year - 1, month=1, day=1)
    with pytest.raises(ValidationError):
        DateOfBirthInputSchema(date_of_birth=date_of_birth)


def test_update_user_schema_dict_excludes_unset() -> None:
    schema = UpdateUserSchema()
    assert schema.model_dump() == {}


def test_update_user_schema_dict_includes_set() -> None:
    birthday = date(year=2000, month=1, day=1)
    schema = UpdateUserSchema(first_name="John", date_of_birth=birthday)
    assert schema.model_dump() == {"first_name": "John", "date_of_birth": birthday}


def test_update_user_schema_with_implicit_none_date_of_birth() -> None:
    schema = UpdateUserSchema(date_of_birth=None)
    assert schema.model_dump() == {"date_of_birth": None}
