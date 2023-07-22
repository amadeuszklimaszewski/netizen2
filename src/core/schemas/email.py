from typing import Any

from pydantic import BaseModel, field_validator, validate_email

from src.settings import settings


class EmailSchema(BaseModel):
    from_email: str = settings.MAIL_FROM

    subject: str
    recipients: tuple[str, ...]

    template_name: str
    context: dict[str, Any]

    @field_validator("from_email")
    @classmethod
    def validate_from_email(cls, email: str) -> str:
        validate_email(email)
        return email

    @field_validator("recipients")
    @classmethod
    def validate_recipients(cls, recipients: tuple[str, ...]) -> tuple[str, ...]:
        for email_ in recipients:
            validate_email(email_)
        return recipients
