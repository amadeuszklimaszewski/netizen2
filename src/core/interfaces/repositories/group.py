import uuid
from abc import ABC, abstractmethod

from src.core.interfaces.repositories.base import BaseRepository
from src.core.models.group import Group, GroupMember, GroupRequest


class GroupRepository(BaseRepository[uuid.UUID, Group], ABC):
    pass


class GroupRequestRepository(BaseRepository[uuid.UUID, GroupRequest], ABC):
    @abstractmethod
    async def get_pending_request_by_user_and_group_id(
        self,
        user_id: uuid.UUID,
        group_id: uuid.UUID,
    ) -> GroupRequest:
        raise NotImplementedError


class GroupMemberRepository(BaseRepository[uuid.UUID, GroupMember], ABC):
    @abstractmethod
    async def get_by_user_and_group_id(
        self,
        user_id: uuid.UUID,
        group_id: uuid.UUID,
    ) -> GroupMember:
        raise NotImplementedError
