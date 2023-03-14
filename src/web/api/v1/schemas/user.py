from datetime import date
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserOutputSchema(BaseModel):
    id: UUID
    email: str
    is_active: bool

    first_name: str | None
    last_name: str | None
    date_of_birth: date | None


class SendPasswordResetEmailSchema(BaseModel):
    email: EmailStr


class PasswordResetSchema(BaseModel):
    password: str
