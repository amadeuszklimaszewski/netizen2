from sqlalchemy import Boolean, Column, Date, DateTime, String, Table, func
from sqlalchemy.dialects.postgresql import UUID

from src.infrastructure.database.metadata import metadata

user_table = Table(
    "user_login_data",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("password_hash", String, nullable=False),
    Column("first_name", String),
    Column("last_name", String),
    Column("date_of_birth", Date),
    Column("email_confirmation_token", String),
    Column("password_reset_token", String),
    Column("password_reset_token_expires_at", DateTime),
    Column("is_active", Boolean, default=False, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now()),
)
