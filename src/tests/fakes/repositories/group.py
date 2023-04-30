from uuid import UUID

from src.core.enums.group import GroupRequestStatus
from src.core.exceptions import AlreadyExistsError, DoesNotExistError
from src.core.filters.group import FilterSet
from src.core.interfaces.repositories.group import (
    GroupMemberRepository,
    GroupRepository,
    GroupRequestRepository,
)
from src.core.models.group import Group, GroupMember, GroupRequest


class FakeGroupRepository(GroupRepository):
    def __init__(self) -> None:
        self.groups: dict[UUID, Group] = {}

    async def get(self, pk: UUID) -> Group:
        try:
            return self.groups[pk]
        except KeyError:
            raise DoesNotExistError("Group does not exist")

    async def get_many(self, filter_set: FilterSet | None = None) -> list[Group]:
        groups = list(self.groups.values())

        if filter_set:
            filters = filter_set.get_filters()
            groups = [
                group for group in groups if all(filter_(group) for filter_ in filters)
            ]

        return groups

    async def persist(self, group: Group) -> None:
        if group.id in self.groups:
            raise AlreadyExistsError("Group already exists")
        self.groups[group.id] = group

    async def persist_many(self, groups: list[Group]) -> None:
        for group in groups:
            if group.id in self.groups:
                raise AlreadyExistsError("Group already exists")
            self.groups[group.id] = group

    async def update(
        self,
        group: Group,
        *_,
        fields_to_update: list[str] | None = None,
    ) -> None:
        self.groups[group.id] = group

    async def delete(self, group: Group) -> None:
        del self.groups[group.id]

    @property
    def _model(self) -> type[Group]:
        return Group


class FakeGroupRequestRepository(GroupRequestRepository):
    def __init__(self) -> None:
        self.group_requests: dict[UUID, GroupRequest] = {}

    async def get(self, pk: UUID) -> GroupRequest:
        try:
            return self.group_requests[pk]
        except KeyError:
            raise DoesNotExistError("Group request does not exist")

    async def get_many(
        self,
        filter_set: FilterSet | None = None,
    ) -> list[GroupRequest]:
        group_requests = list(self.group_requests.values())

        if filter_set:
            filters = filter_set.get_filters()
            group_requests = [
                group_request
                for group_request in group_requests
                if all(filter_(group_request) for filter_ in filters)
            ]

        return group_requests

    async def persist(self, group_request: GroupRequest) -> None:
        if group_request.id in self.group_requests:
            raise AlreadyExistsError("Group request already exists")
        self.group_requests[group_request.id] = group_request

    async def persist_many(self, group_requests: list[GroupRequest]) -> None:
        for group_request in group_requests:
            if group_request.id in self.group_requests:
                raise AlreadyExistsError("Group request already exists")
            self.group_requests[group_request.id] = group_request

    async def update(
        self,
        group_request: GroupRequest,
        *_,
        fields_to_update: list[str] | None = None,
    ) -> None:
        self.group_requests[group_request.id] = group_request

    async def delete(self, group_request: GroupRequest) -> None:
        del self.group_requests[group_request.id]

    async def get_pending_request_by_user_and_group_id(
        self,
        user_id: UUID,
        group_id: UUID,
    ) -> GroupRequest:
        for group_request in self.group_requests.values():
            if (
                group_request.user_id == user_id
                and group_request.group_id == group_id
                and group_request.status == GroupRequestStatus.PENDING
            ):
                return group_request

        raise DoesNotExistError("Pending group request does not exist")

    @property
    def _model(self) -> type[GroupRequest]:
        return GroupRequest


class FakeGroupMemberRepository(GroupMemberRepository):
    def __init__(self) -> None:
        self.group_members: dict[UUID, GroupMember] = {}

    async def get(self, pk: UUID) -> GroupMember:
        try:
            return self.group_members[pk]
        except KeyError:
            raise DoesNotExistError("Group member does not exist")

    async def get_many(
        self,
        filter_set: FilterSet | None = None,
    ) -> list[GroupMember]:
        group_members = list(self.group_members.values())

        if filter_set:
            filters = filter_set.get_filters()
            group_members = [
                group_member
                for group_member in group_members
                if all(filter_(group_member) for filter_ in filters)
            ]

        return group_members

    async def persist(self, group_member: GroupMember) -> None:
        if group_member.id in self.group_members:
            raise AlreadyExistsError("Group member already exists")
        self.group_members[group_member.id] = group_member

    async def persist_many(self, group_members: list[GroupMember]) -> None:
        for group_member in group_members:
            if group_member.id in self.group_members:
                raise AlreadyExistsError("Group member already exists")
            self.group_members[group_member.id] = group_member

    async def update(
        self,
        group_member: GroupMember,
        *_,
        fields_to_update: list[str] | None = None,
    ) -> None:
        self.group_members[group_member.id] = group_member

    async def delete(self, group_member: GroupMember) -> None:
        del self.group_members[group_member.id]

    async def get_by_user_and_group_id(
        self,
        user_id: UUID,
        group_id: UUID,
    ) -> GroupMember:
        for group_member in self.group_members.values():
            if group_member.user_id == user_id and group_member.group_id == group_id:
                return group_member

        raise DoesNotExistError("Group member does not exist")

    @property
    def _model(self) -> type[GroupMember]:
        return GroupMember
