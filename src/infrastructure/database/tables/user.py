from sqlalchemy import Column, DateTime, String, Table, func
from sqlalchemy.dialects.postgresql import UUID

from src.infrastructure.database.metadata import metadata

user_table = Table(
    "users",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, server_default=func.now(), nullable=False),
    Column("activated_at", DateTime, nullable=True),
)
