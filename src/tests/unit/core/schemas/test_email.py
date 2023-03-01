import pytest
from pydantic import ValidationError

from src.core.schemas.email import EmailSchema


def test_email_schema_invalid_from_email():
    with pytest.raises(ValidationError):
        EmailSchema(
            from_email="invalid_email",
            subject="subject",
            recipients=("test@example.com",),
            template_name="template_name",
            context={},
        )


def test_email_schema_invalid_recipients():
    with pytest.raises(ValidationError):
        EmailSchema(
            from_email="test@example.com",
            subject="subject",
            recipients=("invalid_email",),
            template_name="template_name",
            context={},
        )
