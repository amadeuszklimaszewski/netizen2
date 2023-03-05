from datetime import datetime, timedelta
from uuid import uuid4

from src.core.exceptions import (
    AlreadyActiveError,
    ExpiredTokenError,
    InvalidTokenError,
    UserNotActiveError,
)
from src.core.models.base import AppModel
from src.core.utils import get_password_hash


class User(AppModel):
    email: str
    password_hash: str

    is_active: bool = False
    email_confirmation_token: str | None = None
    password_reset_token: str | None = None
    password_reset_token_expires_at: datetime | None = None

    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: datetime | None = None

    def generate_email_confirmation_token(self) -> str:
        self.email_confirmation_token = uuid4().hex
        return self.email_confirmation_token

    def generate_password_reset_token(self) -> str:
        self.password_reset_token = uuid4().hex
        self.password_reset_token_expires_at = datetime.now() + timedelta(hours=1)
        return self.password_reset_token

    def activate(self) -> None:
        if self.is_active:
            raise AlreadyActiveError("User is already active")

        self.is_active = True

    def confirm_email(self, token: str) -> None:
        if self.email_confirmation_token != token:
            raise InvalidTokenError("Invalid token")

        self.email_confirmation_token = None
        self.activate()

    def deactivate(self) -> None:
        if not self.is_active:
            raise UserNotActiveError("User is already inactive")

        self.is_active = False

    def reset_password(self, token: str, new_password: str) -> None:
        if self.password_reset_token != token:
            raise InvalidTokenError("Invalid token")

        if (
            not self.password_reset_token_expires_at
            or self.password_reset_token_expires_at <= datetime.now()
        ):
            raise ExpiredTokenError("Expired token")

        self.password_hash = get_password_hash(new_password)
        self.password_reset_token = None
        self.password_reset_token_expires_at = None

    def get_email_context(self) -> dict[str, str | None]:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "email_confirmation_token": self.email_confirmation_token,
            "password_reset_token": self.password_reset_token,
        }
