from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Table, func
from sqlalchemy.dialects.postgresql import UUID

from src.constants import constants
from src.core.enums.group import GroupRequestStatus
from src.infrastructure.database.metadata import metadata

group_table = Table(
    "group",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "name",
        String(constants.MAX_GROUP_NAME_LENGTH),
        nullable=False,
    ),
    Column(
        "description",
        String(constants.MAX_GROUP_DESCRIPTION_LENGTH),
        nullable=True,
    ),
    Column("is_private", Boolean, default=False, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now()),
)

group_member_table = Table(
    "group_member",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True),
    Column("group_id", UUID(as_uuid=True), ForeignKey("group.id"), primary_key=True),
    Column("is_admin", Boolean, default=False, nullable=False),
    Column("is_owner", Boolean, default=False, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now()),
)

group_request_table = Table(
    "group_request",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True),
    Column("group_id", UUID(as_uuid=True), ForeignKey("group.id"), primary_key=True),
    Column("status", Enum(GroupRequestStatus), nullable=False),
    Column(
        "message",
        String(constants.MAX_GROUP_REQUEST_MESSAGE_LENGTH),
        nullable=True,
    ),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now()),
)
