from typing import Any

from pydantic import BaseModel, Field, validate_email, validator


class CreateUserSchema(BaseModel):
    email: str
    password: str = Field(min_length=8)
    repeat_password: str = Field(min_length=8)

    @validator("email")
    def validate_email(cls, email: str) -> str:
        validate_email(email)
        return email

    @validator("repeat_password")
    def validate_password(cls, repeat_password: str, values: dict[str, Any]) -> str:
        if repeat_password != values["password"]:
            raise ValueError("Passwords do not match")
        return repeat_password
