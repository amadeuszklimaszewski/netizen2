from datetime import date

from pydantic import BaseModel, EmailStr

from src.web.api.v1.schemas.base import BaseOutputSchema


class UserOutputSchema(BaseOutputSchema):
    email: str
    is_active: bool

    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None


class SendPasswordResetEmailSchema(BaseModel):
    email: EmailStr


class PasswordResetSchema(BaseModel):
    password: str
