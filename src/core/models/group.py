from uuid import UUID

from src.core.enums.group import GroupRequestStatus
from src.core.models.base import AppModel


class Group(AppModel):
    name: str
    description: str | None = None
    is_private: bool = False


class GroupMember(AppModel):
    user_id: UUID
    group_id: UUID

    is_admin: bool = False
    is_owner: bool = False


class GroupRequest(AppModel):
    user_id: UUID
    group_id: UUID

    message: str | None = None
    status: GroupRequestStatus = GroupRequestStatus.PENDING
