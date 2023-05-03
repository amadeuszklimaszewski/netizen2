from uuid import UUID

from src.core.models.group import Group, GroupMember, GroupRequest
from src.core.models.user import User


class FakeDatabase:
    def __init__(self) -> None:
        self.users: dict[UUID, User] = {}
        self.groups: dict[UUID, Group] = {}
        self.group_members: dict[UUID, GroupMember] = {}
        self.group_requests: dict[UUID, GroupRequest] = {}
