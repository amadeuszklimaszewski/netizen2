from datetime import date
from uuid import uuid4

import pytest
import pytest_asyncio

from src.core.enums.group import GroupRequestStatus
from src.core.exceptions import (
    AlreadyAGroupMemberError,
    AlreadyAGroupOwnerError,
    AlreadyRequestedToJoinGroupError,
    CannotDeleteAGroupOwnerError,
    CannotLeaveGroupAsOwnerError,
    DoesNotExistError,
    NotAGroupMemberError,
    NotAGroupOwnerError,
    NotAGroupOwnerOrAdminError,
    NotARequestOwnerError,
    RequestNotPendingError,
)
from src.core.filters.group import GroupInputFilters
from src.core.models.group import Group, GroupMember, GroupRequest
from src.core.models.user import User
from src.core.schemas.group import (
    CreateGroupMemberSchema,
    CreateGroupRequestSchema,
    CreateGroupSchema,
    UpdateGroupMemberSchema,
    UpdateGroupRequestSchema,
    UpdateGroupSchema,
)
from src.core.services.group import GroupService


@pytest.fixture
def create_group_schema() -> CreateGroupSchema:
    return CreateGroupSchema(
        name="Test Group Name",
        description="Test description",
        is_private=False,
    )


@pytest.fixture
def update_group_schema() -> UpdateGroupSchema:
    return UpdateGroupSchema(
        name="Updated Group Name",
        description="Updated description",
        is_private=False,
    )


@pytest.fixture
def user() -> User:
    return User(
        email="test@example.com",
        password_hash="password_hash",
        is_active=True,
        is_superuser=False,
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1990, 1, 1),
    )


@pytest.fixture
def other_user() -> User:
    return User(
        email="other@example.com",
        password_hash="password_hash",
        is_active=True,
        is_superuser=False,
        first_name="Jane",
        last_name="Smith",
        date_of_birth=date(1990, 1, 1),
    )


@pytest_asyncio.fixture
async def group(
    user: User,
    create_group_schema: CreateGroupSchema,
    group_service: GroupService,
) -> Group:
    return await group_service.create_group(user.id, create_group_schema)


@pytest_asyncio.fixture
async def other_user_group_member(
    other_user: User,
    group: Group,
    group_service: GroupService,
) -> GroupMember:
    schema = CreateGroupMemberSchema(
        user_id=other_user.id,
        group_id=group.id,
        is_admin=False,
        is_owner=False,
    )
    return await group_service.create_group_member(schema)


@pytest_asyncio.fixture
async def other_user_group_request(
    other_user: User,
    group: Group,
    group_service: GroupService,
) -> GroupRequest:
    schema = CreateGroupRequestSchema(
        message="Test message",
    )
    return await group_service.create_group_request(other_user.id, group.id, schema)


@pytest.mark.asyncio
async def test_create_group(
    user: User,
    create_group_schema: CreateGroupSchema,
    group_service: GroupService,
) -> None:
    group = await group_service.create_group(user.id, create_group_schema)

    assert group.name == create_group_schema.name
    assert group.description == create_group_schema.description
    assert group.is_private == create_group_schema.is_private


@pytest.mark.asyncio
async def test_create_group_creates_member(
    user: User,
    create_group_schema: CreateGroupSchema,
    group_service: GroupService,
) -> None:
    group = await group_service.create_group(user.id, create_group_schema)

    members = await group_service.get_group_members(user.id, group.id)

    assert len(members) == 1
    assert members[0].user_id == user.id
    assert members[0].group_id == group.id
    assert members[0].is_owner is True


@pytest.mark.asyncio
async def test_update_group(
    user: User,
    group: Group,
    update_group_schema: UpdateGroupSchema,
    group_service: GroupService,
) -> None:
    await group_service.update_group(user.id, group.id, update_group_schema)

    result = await group_service.get_group(group.id)

    assert result.name == update_group_schema.name
    assert result.description == update_group_schema.description
    assert result.is_private == update_group_schema.is_private


@pytest.mark.asyncio
async def test_update_group_other_user(
    user: User,
    other_user: User,
    group: Group,
    update_group_schema: UpdateGroupSchema,
    group_service: GroupService,
) -> None:
    with pytest.raises(NotAGroupMemberError):
        await group_service.update_group(other_user.id, group.id, update_group_schema)


@pytest.mark.asyncio
async def test_update_group_other_member(
    user: User,
    other_user: User,
    group: Group,
    other_user_group_member: GroupMember,
    update_group_schema: UpdateGroupSchema,
    group_service: GroupService,
) -> None:
    with pytest.raises(NotAGroupOwnerError):
        await group_service.update_group(other_user.id, group.id, update_group_schema)


@pytest.mark.asyncio
async def test_delete_group(
    user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    await group_service.delete_group(user.id, group.id)

    with pytest.raises(DoesNotExistError):
        await group_service.get_group(group.id)


@pytest.mark.asyncio
async def test_delete_group_other_user(
    other_user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    with pytest.raises(NotAGroupMemberError):
        await group_service.delete_group(other_user.id, group.id)


@pytest.mark.asyncio
async def test_delete_group_other_member(
    other_user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    with pytest.raises(NotAGroupOwnerError):
        await group_service.delete_group(other_user.id, group.id)


@pytest.mark.asyncio
async def test_delete_group_other_member_is_admin(
    other_user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    other_user_group_member.is_admin = True
    with pytest.raises(NotAGroupOwnerError):
        await group_service.delete_group(other_user.id, group.id)


@pytest.mark.asyncio
async def test_get_group(
    group: Group,
    group_service: GroupService,
) -> None:
    result = await group_service.get_group(group.id)

    assert result == group


@pytest.mark.asyncio
async def test_get_groups(
    group: Group,
    group_service: GroupService,
) -> None:
    result = await group_service.get_groups()

    assert len(result) == 1
    assert result[0] == group


@pytest.mark.asyncio
async def test_get_groups_with_filters(
    group: Group,
    group_service: GroupService,
) -> None:
    filters = GroupInputFilters(name__eq=group.name)

    result = await group_service.get_groups(filters)

    assert len(result) == 1
    assert result[0] == group

    filters = GroupInputFilters(name__eq="Other Name")

    result = await group_service.get_groups(filters)

    assert result == []


@pytest.mark.asyncio
async def test_create_group_request(
    other_user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    schema = CreateGroupRequestSchema(message="Test message")

    request = await group_service.create_group_request(other_user.id, group.id, schema)

    assert request.user_id == other_user.id
    assert request.group_id == group.id
    assert request.message == schema.message


@pytest.mark.asyncio
async def test_create_group_request_already_member(
    user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    schema = CreateGroupRequestSchema(message="Test message")

    with pytest.raises(AlreadyAGroupMemberError):
        await group_service.create_group_request(user.id, group.id, schema)


@pytest.mark.asyncio
async def test_create_group_request_already_requested(
    other_user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    schema = CreateGroupRequestSchema(message="Test message")

    await group_service.create_group_request(other_user.id, group.id, schema)

    with pytest.raises(AlreadyRequestedToJoinGroupError):
        await group_service.create_group_request(other_user.id, group.id, schema)


@pytest.mark.asyncio
async def test_update_group_request(
    user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    schema = UpdateGroupRequestSchema(
        status=GroupRequestStatus.ACCEPTED,
    )

    await group_service.update_group_request(
        user.id,
        group.id,
        other_user_group_request.id,
        schema,
    )

    result = await group_service.get_group_request(
        user.id,
        group.id,
        other_user_group_request.id,
    )

    assert result.status == schema.status


@pytest.mark.asyncio
async def test_update_group_request_wrong_group_id(
    user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    schema = UpdateGroupRequestSchema(
        status=GroupRequestStatus.ACCEPTED,
    )

    with pytest.raises(DoesNotExistError):
        await group_service.update_group_request(
            user.id,
            uuid4(),
            other_user_group_request.id,
            schema,
        )


@pytest.mark.asyncio
async def test_update_group_request_wrong_request_id(
    user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    schema = UpdateGroupRequestSchema(
        status=GroupRequestStatus.ACCEPTED,
    )

    with pytest.raises(DoesNotExistError):
        await group_service.update_group_request(
            user.id,
            group.id,
            uuid4(),
            schema,
        )


@pytest.mark.asyncio
async def test_update_group_request_wrong_user_id(
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    schema = UpdateGroupRequestSchema(
        status=GroupRequestStatus.ACCEPTED,
    )

    with pytest.raises(DoesNotExistError):
        await group_service.update_group_request(
            uuid4(),
            group.id,
            other_user_group_request.id,
            schema,
        )


@pytest.mark.asyncio
async def test_update_group_request_not_admin_or_owner(
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    request_user = User(
        email="member@example.com",
        password_hash="password",
        is_active=True,
        date_of_birth=date(1990, 1, 1),
    )
    create_member_schema = CreateGroupMemberSchema(
        user_id=request_user.id,
        group_id=group.id,
    )
    await group_service.create_group_member(create_member_schema)

    update_schema = UpdateGroupRequestSchema(
        status=GroupRequestStatus.ACCEPTED,
    )

    with pytest.raises(NotAGroupOwnerOrAdminError):
        await group_service.update_group_request(
            request_user.id,
            group.id,
            other_user_group_request.id,
            update_schema,
        )


@pytest.mark.asyncio
async def test_update_group_request_not_pending(
    user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    update_schema = UpdateGroupRequestSchema(
        status=GroupRequestStatus.ACCEPTED,
    )

    await group_service.update_group_request(
        user.id,
        group.id,
        other_user_group_request.id,
        update_schema,
    )

    with pytest.raises(RequestNotPendingError):
        await group_service.update_group_request(
            user.id,
            group.id,
            other_user_group_request.id,
            update_schema,
        )


@pytest.mark.asyncio
async def test_update_group_request_accepted(
    user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    update_schema = UpdateGroupRequestSchema(
        status=GroupRequestStatus.ACCEPTED,
    )

    await group_service.update_group_request(
        user.id,
        group.id,
        other_user_group_request.id,
        update_schema,
    )

    members = await group_service.get_group_members(user.id, group.id)

    assert len(members) == 2


@pytest.mark.asyncio
async def test_update_group_request_declined(
    user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    update_schema = UpdateGroupRequestSchema(
        status=GroupRequestStatus.DECLINED,
    )

    await group_service.update_group_request(
        user.id,
        group.id,
        other_user_group_request.id,
        update_schema,
    )

    members = await group_service.get_group_members(user.id, group.id)

    assert len(members) == 1
    assert members[0].user_id == user.id


@pytest.mark.asyncio
async def test_delete_group_request(
    other_user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    await group_service.delete_group_request(
        other_user.id,
        group.id,
        other_user_group_request.id,
    )

    with pytest.raises(DoesNotExistError):
        await group_service.get_group_request(
            other_user.id,
            group.id,
            other_user_group_request.id,
        )


@pytest.mark.asyncio
async def test_delete_group_request_by_non_owner(
    other_user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.delete_group_request(
            uuid4(),
            group.id,
            other_user_group_request.id,
        )


@pytest.mark.asyncio
async def test_delete_group_request_wrong_group_id(
    other_user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.delete_group_request(
            other_user.id,
            uuid4(),
            other_user_group_request.id,
        )


@pytest.mark.asyncio
async def test_delete_group_request_wrong_request_id(
    other_user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.delete_group_request(
            other_user.id,
            group.id,
            uuid4(),
        )


@pytest.mark.asyncio
async def test_delete_group_request_wrong_user_id(
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.delete_group_request(
            uuid4(),
            group.id,
            other_user_group_request.id,
        )


@pytest.mark.asyncio
async def test_delete_group_request_not_owner_of_request(
    user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.delete_group_request(
            user.id,
            group.id,
            other_user_group_request.id,
        )


@pytest.mark.asyncio
async def test_delete_group_request_not_pending(
    user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    update_schema = UpdateGroupRequestSchema(
        status=GroupRequestStatus.ACCEPTED,
    )

    await group_service.update_group_request(
        user.id,
        group.id,
        other_user_group_request.id,
        update_schema,
    )

    with pytest.raises(RequestNotPendingError):
        await group_service.delete_group_request(
            other_user_group_request.user_id,
            group.id,
            other_user_group_request.id,
        )


@pytest.mark.asyncio
async def test_get_group_request(
    user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    request = await group_service.get_group_request(
        user.id,
        group.id,
        other_user_group_request.id,
    )

    assert request.id == other_user_group_request.id


@pytest.mark.asyncio
async def test_get_group_request_wrong_group_id(
    user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.get_group_request(
            user.id,
            uuid4(),
            other_user_group_request.id,
        )


@pytest.mark.asyncio
async def test_get_group_request_by_not_request_owner(
    user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    with pytest.raises(NotARequestOwnerError):
        await group_service.get_group_request(
            uuid4(),
            group.id,
            other_user_group_request.id,
        )


@pytest.mark.asyncio
async def test_get_group_requests_by_admin_or_owner(
    user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    requests = await group_service.get_group_requests(user.id, group.id)

    assert len(requests) == 1
    assert requests[0].id == other_user_group_request.id


@pytest.mark.asyncio
async def test_get_group_requests_wrong_group_id(
    user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    requests = await group_service.get_group_requests(user.id, uuid4())

    assert requests == []


@pytest.mark.asyncio
async def test_get_group_requests_by_requesting_user(
    other_user: User,
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    requests = await group_service.get_group_requests(other_user.id, group.id)

    assert len(requests) == 1
    assert requests[0].id == other_user_group_request.id


@pytest.mark.asyncio
async def test_get_group_requests_by_member(
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    request_user = User(
        email="member@example.com",
        password_hash="password",
        is_active=True,
        date_of_birth=date(1990, 1, 1),
    )
    create_member_schema = CreateGroupMemberSchema(
        user_id=request_user.id,
        group_id=group.id,
    )
    await group_service.create_group_member(create_member_schema)

    with pytest.raises(NotAGroupOwnerOrAdminError):
        await group_service.get_group_requests(request_user.id, group.id)


@pytest.mark.asyncio
async def test_get_group_requests_by_non_member(
    group: Group,
    other_user_group_request: GroupRequest,
    group_service: GroupService,
) -> None:
    request_user = User(
        email="non_member@example.com",
        password_hash="password",
        is_active=True,
        date_of_birth=date(1990, 1, 1),
    )

    results = await group_service.get_group_requests(request_user.id, group.id)

    assert results == []


@pytest.mark.asyncio
async def test_create_group_member(
    other_user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    schema = CreateGroupMemberSchema(
        user_id=other_user.id,
        group_id=group.id,
        is_admin=False,
        is_owner=False,
    )
    member = await group_service.create_group_member(schema)

    assert member.user_id == schema.user_id
    assert member.group_id == schema.group_id
    assert member.is_admin == schema.is_admin
    assert member.is_owner == schema.is_owner


@pytest.mark.asyncio
async def test_create_group_member_already_member(
    user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    schema = CreateGroupMemberSchema(
        user_id=user.id,
        group_id=group.id,
    )

    with pytest.raises(AlreadyAGroupMemberError):
        await group_service.create_group_member(schema)


@pytest.mark.asyncio
async def test_create_group_member_wrong_group_id(
    other_user: User,
    group_service: GroupService,
) -> None:
    schema = CreateGroupMemberSchema(
        user_id=other_user.id,
        group_id=uuid4(),
    )

    with pytest.raises(DoesNotExistError):
        await group_service.create_group_member(schema)


@pytest.mark.asyncio
async def test_update_group_member(
    user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    schema = UpdateGroupMemberSchema(
        is_admin=True,
    )

    await group_service.update_group_member(
        user.id,
        group.id,
        other_user_group_member.id,
        schema,
    )
    member = await group_service.get_group_member(
        request_user_id=user.id,
        group_id=group.id,
        member_id=other_user_group_member.id,
    )

    assert member.is_admin == schema.is_admin


@pytest.mark.asyncio
async def test_update_group_member_wrong_group_id(
    user: User,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    schema = UpdateGroupMemberSchema(
        is_admin=True,
    )

    with pytest.raises(DoesNotExistError):
        await group_service.update_group_member(
            user.id,
            uuid4(),
            other_user_group_member.id,
            schema,
        )


@pytest.mark.asyncio
async def test_update_group_member_wrong_member_id(
    user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    schema = UpdateGroupMemberSchema(
        is_admin=True,
    )

    with pytest.raises(DoesNotExistError):
        await group_service.update_group_member(
            user.id,
            group.id,
            uuid4(),
            schema,
        )


@pytest.mark.asyncio
async def test_update_group_member_by_non_admin_member(
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    request_user = User(
        email="member@example.com",
        password_hash="password",
        is_active=True,
        date_of_birth=date(1990, 1, 1),
    )
    create_member_schema = CreateGroupMemberSchema(
        user_id=request_user.id,
        group_id=group.id,
    )
    await group_service.create_group_member(create_member_schema)

    schema = UpdateGroupMemberSchema(
        is_admin=True,
    )

    with pytest.raises(NotAGroupOwnerError):
        await group_service.update_group_member(
            request_user.id,
            group.id,
            other_user_group_member.id,
            schema,
        )


@pytest.mark.asyncio
async def test_update_group_member_by_non_member(
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    request_user = User(
        email="non_member@example.com",
        password_hash="password",
        is_active=True,
        date_of_birth=date(1990, 1, 1),
    )

    schema = UpdateGroupMemberSchema(
        is_admin=True,
    )

    with pytest.raises(NotAGroupMemberError):
        await group_service.update_group_member(
            request_user.id,
            group.id,
            other_user_group_member.id,
            schema,
        )


@pytest.mark.asyncio
async def test_update_group_member_owner(
    user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    members = await group_service.get_group_members(user.id, group.id)
    owner = next(member for member in members if member.is_owner)

    schema = UpdateGroupMemberSchema(
        is_admin=True,
    )

    with pytest.raises(NotAGroupOwnerError):
        await group_service.update_group_member(
            other_user_group_member.user_id,
            group.id,
            owner.id,
            schema,
        )


@pytest.mark.asyncio
async def test_update_admin_group_member_by_admin_member(
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    request_user = User(
        email="member@example.com",
        password_hash="password",
        is_active=True,
        date_of_birth=date(1990, 1, 1),
    )
    create_member_schema = CreateGroupMemberSchema(
        user_id=request_user.id,
        group_id=group.id,
        is_admin=True,
    )
    await group_service.create_group_member(create_member_schema)
    other_user_group_member.is_admin = True

    schema = UpdateGroupMemberSchema(
        is_admin=True,
    )

    with pytest.raises(NotAGroupOwnerError):
        await group_service.update_group_member(
            request_user.id,
            group.id,
            other_user_group_member.id,
            schema,
        )


@pytest.mark.asyncio
async def test_change_group_owner(
    user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    members = await group_service.get_group_members(user.id, group.id)
    owner = next(member for member in members if member.is_owner)

    await group_service.change_group_owner(
        user.id,
        group.id,
        other_user_group_member.id,
    )
    member = await group_service.get_group_member(
        request_user_id=user.id,
        group_id=group.id,
        member_id=other_user_group_member.id,
    )

    assert member.is_owner
    assert not owner.is_owner


@pytest.mark.asyncio
async def test_change_group_owner_wrong_group_id(
    user: User,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.change_group_owner(
            user.id,
            uuid4(),
            other_user_group_member.id,
        )


@pytest.mark.asyncio
async def test_change_group_owner_wrong_member_id(
    user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.change_group_owner(
            user.id,
            group.id,
            uuid4(),
        )


@pytest.mark.asyncio
async def test_change_group_owner_by_non_admin_member(
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    request_user = User(
        email="member@example.com",
        password_hash="password",
        is_active=True,
        date_of_birth=date(1990, 1, 1),
    )
    create_member_schema = CreateGroupMemberSchema(
        user_id=request_user.id,
        group_id=group.id,
    )
    await group_service.create_group_member(create_member_schema)

    with pytest.raises(NotAGroupOwnerError):
        await group_service.change_group_owner(
            request_user.id,
            group.id,
            other_user_group_member.id,
        )


@pytest.mark.asyncio
async def test_change_group_owner_by_non_member(
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    request_user = User(
        email="admin@example.com",
        password_hash="password",
        is_active=True,
        date_of_birth=date(1990, 1, 1),
    )

    with pytest.raises(NotAGroupMemberError):
        await group_service.change_group_owner(
            request_user.id,
            group.id,
            other_user_group_member.id,
        )


@pytest.mark.asyncio
async def test_change_group_owner_to_existing_owner(
    user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    members = await group_service.get_group_members(user.id, group.id)
    owner = next(member for member in members if member.is_owner)

    with pytest.raises(AlreadyAGroupOwnerError):
        await group_service.change_group_owner(
            user.id,
            group.id,
            owner.id,
        )


@pytest.mark.asyncio
async def test_delete_group_member(
    user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    await group_service.delete_group_member(
        user.id,
        group.id,
        other_user_group_member.id,
    )

    with pytest.raises(DoesNotExistError):
        await group_service.get_group_member(
            request_user_id=user.id,
            group_id=group.id,
            member_id=other_user_group_member.id,
        )


@pytest.mark.asyncio
async def test_delete_group_member_wrong_group_id(
    user: User,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.delete_group_member(
            user.id,
            uuid4(),
            other_user_group_member.id,
        )


@pytest.mark.asyncio
async def test_delete_group_member_wrong_member_id(
    user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.delete_group_member(
            user.id,
            group.id,
            uuid4(),
        )


@pytest.mark.asyncio
async def test_delete_group_member_by_non_admin_member(
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    request_user = User(
        email="member@example.com",
        password_hash="password",
        is_active=True,
        date_of_birth=date(1990, 1, 1),
    )
    create_member_schema = CreateGroupMemberSchema(
        user_id=request_user.id,
        group_id=group.id,
    )
    await group_service.create_group_member(create_member_schema)

    with pytest.raises(NotAGroupOwnerOrAdminError):
        await group_service.delete_group_member(
            request_user.id,
            group.id,
            other_user_group_member.id,
        )


@pytest.mark.asyncio
async def test_delete_group_member_by_non_member(
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    request_user = User(
        email="non_member@example.com",
        password_hash="password",
        is_active=True,
        date_of_birth=date(1990, 1, 1),
    )

    with pytest.raises(NotAGroupMemberError):
        await group_service.delete_group_member(
            request_user.id,
            group.id,
            other_user_group_member.id,
        )


@pytest.mark.asyncio
async def test_delete_group_member_owner(
    user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    members = await group_service.get_group_members(user.id, group.id)
    owner = next(member for member in members if member.is_owner)

    with pytest.raises(CannotDeleteAGroupOwnerError):
        await group_service.delete_group_member(
            user.id,
            group.id,
            owner.id,
        )


@pytest.mark.asyncio
async def test_delete_group_member_admin_by_other_admin(
    group: Group,
    group_service: GroupService,
) -> None:
    request_admin_user = User(
        email="admin@example.com",
        password_hash="password",
        is_active=True,
        date_of_birth=date(1990, 1, 1),
    )
    admin_member_schema = CreateGroupMemberSchema(
        user_id=request_admin_user.id,
        group_id=group.id,
        is_admin=True,
    )

    other_admin_user = User(
        email="other_admin@example.com",
        password_hash="password",
        is_active=True,
        date_of_birth=date(1990, 1, 1),
    )
    other_admin_member_schema = CreateGroupMemberSchema(
        user_id=other_admin_user.id,
        group_id=group.id,
        is_admin=True,
    )

    admin = await group_service.create_group_member(admin_member_schema)
    other_admin = await group_service.create_group_member(other_admin_member_schema)

    with pytest.raises(NotAGroupOwnerError):
        await group_service.delete_group_member(
            admin.user_id,
            group.id,
            other_admin.id,
        )


@pytest.mark.asyncio
async def test_leave_group_by_owner(
    user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    with pytest.raises(CannotLeaveGroupAsOwnerError):
        await group_service.leave_group(
            request_user_id=user.id,
            group_id=group.id,
        )


@pytest.mark.asyncio
async def test_leave_group_by_non_owner_member(
    user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:

    await group_service.leave_group(
        request_user_id=other_user_group_member.user_id,
        group_id=group.id,
    )

    with pytest.raises(DoesNotExistError):
        await group_service.get_group_member(
            request_user_id=user.id,
            group_id=group.id,
            member_id=other_user_group_member.id,
        )


@pytest.mark.asyncio
async def test_leave_group_by_non_member(
    other_user: User,
    group: Group,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.leave_group(
            request_user_id=other_user.id,
            group_id=group.id,
        )


@pytest.mark.asyncio
async def test_get_non_private_group_member_by_non_member(
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    member = await group_service.get_group_member(
        request_user_id=uuid4(),
        group_id=group.id,
        member_id=other_user_group_member.id,
    )

    assert member.user_id == other_user_group_member.user_id
    assert member.group_id == group.id


@pytest.mark.asyncio
async def test_get_private_group_member_by_non_member(
    user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    group_schema = UpdateGroupSchema(is_private=True)  # type: ignore
    await group_service.update_group(user.id, group.id, group_schema)

    with pytest.raises(NotAGroupMemberError):
        await group_service.get_group_member(
            request_user_id=uuid4(),
            group_id=group.id,
            member_id=other_user_group_member.id,
        )


@pytest.mark.asyncio
async def test_get_private_group_member_by_member(
    user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    group_schema = UpdateGroupSchema(is_private=True)  # type: ignore
    await group_service.update_group(user.id, group.id, group_schema)

    member = await group_service.get_group_member(
        request_user_id=user.id,
        group_id=group.id,
        member_id=other_user_group_member.id,
    )

    assert member.user_id == other_user_group_member.user_id
    assert member.group_id == group.id


@pytest.mark.asyncio
async def test_get_group_member_invalid_group_id(
    user: User,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.get_group_member(
            request_user_id=user.id,
            group_id=uuid4(),
            member_id=other_user_group_member.id,
        )


@pytest.mark.asyncio
async def test_get_group_member_invalid_member_id(
    user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.get_group_member(
            request_user_id=user.id,
            group_id=group.id,
            member_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_get_group_members(
    user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    members = await group_service.get_group_members(
        request_user_id=user.id,
        group_id=group.id,
    )

    assert len(members) == 2
    assert members[0].user_id == user.id
    assert members[1].user_id == other_user_group_member.user_id


@pytest.mark.asyncio
async def test_get_group_members_invalid_group_id(
    user: User,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    with pytest.raises(DoesNotExistError):
        await group_service.get_group_members(
            request_user_id=user.id,
            group_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_get_group_members_by_non_member(
    user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    members = await group_service.get_group_members(
        request_user_id=uuid4(),
        group_id=group.id,
    )

    assert len(members) == 2
    assert members[0].user_id == user.id
    assert members[1].user_id == other_user_group_member.user_id


@pytest.mark.asyncio
async def test_get_group_members_by_non_member_private_group(
    user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    group_schema = UpdateGroupSchema(is_private=True)  # type: ignore
    await group_service.update_group(user.id, group.id, group_schema)

    with pytest.raises(NotAGroupMemberError):
        await group_service.get_group_members(
            request_user_id=uuid4(),
            group_id=group.id,
        )


@pytest.mark.asyncio
async def test_get_group_members_by_member_private_group(
    user: User,
    group: Group,
    other_user_group_member: GroupMember,
    group_service: GroupService,
) -> None:
    group_schema = UpdateGroupSchema(is_private=True)  # type: ignore
    await group_service.update_group(user.id, group.id, group_schema)

    members = await group_service.get_group_members(
        request_user_id=user.id,
        group_id=group.id,
    )

    assert len(members) == 2
    assert members[0].user_id == user.id
    assert members[1].user_id == other_user_group_member.user_id
