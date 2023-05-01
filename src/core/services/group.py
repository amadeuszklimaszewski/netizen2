from uuid import UUID

from src.core.enums.group import GroupRequestStatus
from src.core.exceptions import (
    AlreadyExistsError,
    DoesNotExistError,
    PermissionDeniedError,
)
from src.core.filters.group import (
    GroupFilterSet,
    GroupInputFilters,
    GroupMemberFilterSet,
    GroupMemberInputFilters,
    GroupRequestFilterSet,
    GroupRequestInputFilters,
)
from src.core.interfaces.repositories.group import (
    GroupMemberRepository,
    GroupRepository,
    GroupRequestRepository,
)
from src.core.models.group import Group, GroupMember, GroupRequest
from src.core.schemas.group import (
    CreateGroupMemberSchema,
    CreateGroupRequestSchema,
    CreateGroupSchema,
    UpdateGroupMemberSchema,
    UpdateGroupRequestSchema,
    UpdateGroupSchema,
)


class GroupService:
    def __init__(
        self,
        group_repository: GroupRepository,
        member_repository: GroupMemberRepository,
        request_repository: GroupRequestRepository,
    ) -> None:
        self.group_repository = group_repository
        self.member_repository = member_repository
        self.request_repository = request_repository

    async def create_group(self, user_id: UUID, schema: CreateGroupSchema) -> Group:
        group = Group(**schema.dict())
        member = GroupMember(
            user_id=user_id,
            group_id=group.id,
            is_owner=True,
        )

        await self.group_repository.persist(group)
        await self.member_repository.persist(member)

        return group

    async def update_group(
        self,
        request_user_id: UUID,
        group_id: UUID,
        schema: UpdateGroupSchema,
    ) -> None:
        group = await self.group_repository.get(group_id)
        try:
            member = await self.member_repository.get_by_user_and_group_id(
                user_id=request_user_id,
                group_id=group_id,
            )
        except DoesNotExistError:
            raise PermissionDeniedError("Only group members can update group")

        if not member.is_owner:
            raise PermissionDeniedError("Only group owner can update group")

        fields_to_update = []
        for key, value in schema.dict().items():
            setattr(group, key, value)
            fields_to_update.append(key)

        await self.group_repository.update(group, fields_to_update)

    async def delete_group(self, request_user_id: UUID, group_id: UUID) -> None:
        group = await self.group_repository.get(group_id)

        try:
            member = await self.member_repository.get_by_user_and_group_id(
                user_id=request_user_id,
                group_id=group_id,
            )
        except DoesNotExistError:
            raise PermissionDeniedError("Is not a member of the group")

        if not member.is_owner:
            raise PermissionDeniedError("Only the owner can delete a group")

        await self.group_repository.delete(group)

    async def get_group(self, group_id: UUID) -> Group:
        return await self.group_repository.get(pk=group_id)

    async def get_groups(
        self,
        input_filters: GroupInputFilters | None = None,
    ) -> list[Group]:
        if input_filters is None:
            input_filters = GroupInputFilters()

        filter_set = GroupFilterSet(**input_filters.dict())
        return await self.group_repository.get_many(filter_set)

    async def create_group_request(
        self,
        user_id: UUID,
        group_id: UUID,
        schema: CreateGroupRequestSchema,
    ) -> GroupRequest:
        try:
            await self.request_repository.get_pending_request_by_user_and_group_id(
                user_id=user_id,
                group_id=group_id,
            )
            raise AlreadyExistsError("Already requested to join the group")
        except DoesNotExistError:
            pass

        try:
            await self.member_repository.get_by_user_and_group_id(
                user_id=user_id,
                group_id=group_id,
            )
            raise AlreadyExistsError("Already a member of the group")
        except DoesNotExistError:
            pass

        group_request = GroupRequest(
            user_id=user_id,
            group_id=group_id,
            **schema.dict(),
        )
        await self.request_repository.persist(group_request)
        return group_request

    async def update_group_request(
        self,
        request_user_id: UUID,
        group_id: UUID,
        request_id: UUID,
        schema: UpdateGroupRequestSchema,
    ) -> None:
        group_request = await self.request_repository.get(pk=request_id)
        if group_request.group_id != group_id:
            raise DoesNotExistError("Invalid request id")

        member = await self.member_repository.get_by_user_and_group_id(
            user_id=request_user_id,
            group_id=group_id,
        )

        if not (member.is_owner or member.is_admin):
            raise PermissionDeniedError("Only group owner or admin can update requests")

        if group_request.status != GroupRequestStatus.PENDING:
            raise PermissionDeniedError("Request is no longer pending")

        group_request.status = schema.status
        await self.request_repository.update(group_request, ["status"])

        if schema.status == GroupRequestStatus.DECLINED:
            return

        group_member_schema = CreateGroupMemberSchema(
            user_id=group_request.user_id,
            group_id=group_request.group_id,
        )
        await self.create_group_member(group_member_schema)

    async def delete_group_request(
        self,
        request_user_id: UUID,
        group_id: UUID,
        request_id: UUID,
    ) -> None:
        group_request = await self.request_repository.get(pk=request_id)

        if group_request.group_id != group_id:
            raise DoesNotExistError("Invalid request id")

        if group_request.user_id != request_user_id:
            raise DoesNotExistError("Invalid request id")

        if group_request.status != GroupRequestStatus.PENDING:
            raise DoesNotExistError("Request is no longer pending")

        await self.request_repository.delete(group_request)

    async def get_group_request(
        self,
        request_user_id: UUID,
        group_id: UUID,
        request_id: UUID,
    ) -> GroupRequest:
        group_request = await self.request_repository.get(pk=request_id)

        if group_request.group_id != group_id:
            raise PermissionDeniedError("Invalid request id")

        try:
            member = await self.member_repository.get_by_user_and_group_id(
                user_id=request_user_id,
                group_id=group_id,
            )
            if not (member.is_admin or member.is_owner):
                raise PermissionDeniedError("Not an admin or owner of the group")
        except DoesNotExistError:
            if group_request.user_id != request_user_id:
                raise PermissionDeniedError("Only the request owner can view it")

        return group_request

    async def get_group_requests(
        self,
        request_user_id: UUID,
        group_id: UUID,
        input_filters: GroupRequestInputFilters | None = None,
    ) -> list[GroupRequest]:
        if input_filters is None:
            input_filters = GroupRequestInputFilters()

        filter_set = GroupRequestFilterSet(
            group_id__eq=group_id,
            user_id__eq=None,
            **input_filters.dict(),
        )

        try:
            member = await self.member_repository.get_by_user_and_group_id(
                user_id=request_user_id,
                group_id=group_id,
            )
            if not (member.is_admin or member.is_owner):
                raise PermissionDeniedError("Not an admin or owner of the group")

        except DoesNotExistError:
            filter_set.user_id__eq = request_user_id

        return await self.request_repository.get_many(filter_set)

    async def create_group_member(
        self,
        schema: CreateGroupMemberSchema,
    ) -> GroupMember:
        await self.group_repository.get(pk=schema.group_id)

        try:
            await self.member_repository.get_by_user_and_group_id(
                user_id=schema.user_id,
                group_id=schema.group_id,
            )
            raise AlreadyExistsError("Already a member of the group")
        except DoesNotExistError:
            pass

        group_member = GroupMember(**schema.dict())
        await self.member_repository.persist(group_member)
        return group_member

    async def update_group_member(
        self,
        request_user_id: UUID,
        group_id: UUID,
        member_id: UUID,
        schema: UpdateGroupMemberSchema,
    ) -> None:
        await self.group_repository.get(pk=group_id)

        try:
            member = await self.member_repository.get_by_user_and_group_id(
                user_id=request_user_id,
                group_id=group_id,
            )
        except DoesNotExistError:
            raise PermissionDeniedError("Not a member of the group")

        if not member.is_owner:
            raise PermissionDeniedError("Only a group owner can update a member")

        member_to_update = await self.member_repository.get(pk=member_id)

        if member_to_update.is_admin == schema.is_admin:
            return

        member_to_update.is_admin = schema.is_admin
        await self.member_repository.update(member_to_update, ["is_admin"])

    async def change_group_owner(
        self,
        request_user_id: UUID,
        group_id: UUID,
        member_id: UUID,
    ) -> None:
        await self.group_repository.get(pk=group_id)

        try:
            member = await self.member_repository.get_by_user_and_group_id(
                user_id=request_user_id,
                group_id=group_id,
            )
        except DoesNotExistError:
            raise PermissionDeniedError("Not a member of the group")

        member_to_update = await self.member_repository.get(pk=member_id)

        if not member.is_owner:
            raise PermissionDeniedError("Only the owner can change the owner")

        if member_to_update.user_id == request_user_id:
            raise PermissionDeniedError("Cannot change yourself to owner")

        member.is_owner = False
        member_to_update.is_owner = True

        await self.member_repository.update(member, ["is_owner"])
        await self.member_repository.update(member_to_update, ["is_owner"])

    async def delete_group_member(
        self,
        request_user_id: UUID,
        group_id: UUID,
        member_id: UUID,
    ) -> None:
        await self.group_repository.get(pk=group_id)

        try:
            member = await self.member_repository.get_by_user_and_group_id(
                user_id=request_user_id,
                group_id=group_id,
            )
        except DoesNotExistError:
            raise PermissionDeniedError("Not a member of the group")

        if not (member.is_admin or member.is_owner):
            raise PermissionDeniedError("Only an admin or owner can delete a member")

        member_to_delete = await self.member_repository.get(pk=member_id)

        if member_to_delete.is_owner:
            raise PermissionDeniedError("Cannot delete a group owner")

        if member_to_delete.is_admin and not member.is_owner:
            raise PermissionDeniedError("Only the owner can delete a group admin")

        await self.member_repository.delete(member_to_delete)

    async def leave_group(
        self,
        request_user_id: UUID,
        group_id: UUID,
    ) -> None:
        member = await self.member_repository.get_by_user_and_group_id(
            user_id=request_user_id,
            group_id=group_id,
        )

        if member.is_owner:
            raise PermissionDeniedError("Cannot leave as owner")

        await self.member_repository.delete(member)

    async def get_group_member(
        self,
        request_user_id: UUID,
        group_id: UUID,
        member_id: UUID,
    ) -> GroupMember:
        group = await self.group_repository.get(pk=group_id)

        try:
            await self.member_repository.get_by_user_and_group_id(
                user_id=request_user_id,
                group_id=group_id,
            )
        except DoesNotExistError:
            if group.is_private:
                raise PermissionDeniedError("Not a member of the group")

        member = await self.member_repository.get(pk=member_id)
        if member.group_id != group_id:
            raise DoesNotExistError("Invalid member id")

        return member

    async def get_group_members(
        self,
        request_user_id: UUID,
        group_id: UUID,
        filters: GroupMemberInputFilters | None = None,
    ) -> list[GroupMember]:
        if filters is None:
            filters = GroupMemberInputFilters()

        filter_set = GroupMemberFilterSet(
            group_id__eq=group_id,
            user_id__eq=None,
            **filters.dict(),
        )

        group = await self.group_repository.get(pk=group_id)

        try:
            await self.member_repository.get_by_user_and_group_id(
                user_id=request_user_id,
                group_id=group_id,
            )
        except DoesNotExistError:
            if group.is_private:
                raise PermissionDeniedError("Not a member of the group")

        return await self.member_repository.get_many(filter_set)
