from datetime import date, datetime

from pydantic import (
    BaseModel,
    Field,
    FieldValidationInfo,
    field_validator,
    validate_email,
)

from src.core.schemas.base import BaseUpdateSchema
from src.settings import settings


class DateOfBirthInputSchema(BaseModel):
    date_of_birth: date

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, date_of_birth: date) -> date:
        if date_of_birth is None:
            return date_of_birth

        if date_of_birth > datetime.now().date():
            raise ValueError("Date of birth cannot be in the future")
        if date_of_birth.year < settings.MINIMUM_YEAR_OF_BIRTH:
            raise ValueError(
                f"Date of birth cannot be before {settings.MINIMUM_YEAR_OF_BIRTH}",
            )
        if datetime.now().date().year - date_of_birth.year < settings.MINIMUM_AGE:
            raise ValueError(
                f"You must be at least {settings.MINIMUM_AGE} years old",
            )

        return date_of_birth


class CreateUserSchema(DateOfBirthInputSchema):
    email: str
    password: str = Field(min_length=8)
    repeat_password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        validate_email(email)
        return email

    @field_validator("repeat_password")
    @classmethod
    def validate_password(cls, repeat_password: str, info: FieldValidationInfo) -> str:
        if repeat_password != info.data["password"]:
            raise ValueError("Passwords do not match")
        return repeat_password


class UpdateUserSchema(DateOfBirthInputSchema, BaseUpdateSchema):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None  # type: ignore
