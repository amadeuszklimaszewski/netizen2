from uuid import UUID

from src.core.enums.group import GroupRequestStatus
from src.web.api.v1.schemas.base import BaseOutputSchema


class GroupOutputSchema(BaseOutputSchema):
    name: str
    description: str | None
    is_private: bool


class GroupMemberOutputSchema(BaseOutputSchema):
    user_id: UUID
    group_id: UUID

    is_admin: bool
    is_owner: bool


class GroupRequestOutputSchema(BaseOutputSchema):
    user_id: UUID
    group_id: UUID

    message: str | None
    status: GroupRequestStatus
