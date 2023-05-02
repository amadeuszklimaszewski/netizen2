import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient, Response

from src.core.enums.group import GroupRequestStatus
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
    schema = CreateGroupRequestSchema(message="Test message")
    return await group_service.create_group_request(other_user.id, group.id, schema)


@pytest.mark.asyncio
async def test_create_group(
    client: AsyncClient,
    user_bearer_token_header: dict[str, str],
    create_group_schema: CreateGroupSchema,
) -> None:
    response: Response = await client.post(
        "/groups/",
        headers=user_bearer_token_header,
        json=create_group_schema.dict(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["id"] is not None


@pytest.mark.asyncio
async def test_update_group(
    client: AsyncClient,
    user_bearer_token_header: dict[str, str],
    group: Group,
    update_group_schema: UpdateGroupSchema,
) -> None:
    response: Response = await client.patch(
        f"/groups/{group.id}/",
        headers=user_bearer_token_header,
        json=update_group_schema.dict(),
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == str(group.id)


@pytest.mark.asyncio
async def test_delete_group(
    client: AsyncClient,
    user: User,
    user_bearer_token_header: dict[str, str],
    group: Group,
) -> None:
    response: Response = await client.delete(
        f"/groups/{group.id}/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_get_groups(
    client: AsyncClient,
    user_bearer_token_header: dict[str, str],
    group: Group,
) -> None:
    response: Response = await client.get(
        "/groups/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_group_by_id(
    client: AsyncClient,
    user_bearer_token_header: dict[str, str],
    group: Group,
) -> None:
    response: Response = await client.get(
        f"/groups/{group.id}/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == str(group.id)
    assert body["name"] == group.name
    assert body["description"] == group.description
    assert body["is_private"] == group.is_private


@pytest.mark.asyncio
async def test_update_group_member(
    client: AsyncClient,
    user_bearer_token_header: dict[str, str],
    group: Group,
    other_user_group_member: GroupMember,
) -> None:
    schema = UpdateGroupMemberSchema(is_admin=True)
    response: Response = await client.patch(
        f"/groups/{group.id}/members/{other_user_group_member.id}/",
        headers=user_bearer_token_header,
        json=schema.dict(),
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == str(other_user_group_member.id)


@pytest.mark.asyncio
async def test_delete_group_member(
    client: AsyncClient,
    user_bearer_token_header: dict[str, str],
    group: Group,
    other_user_group_member: GroupMember,
) -> None:
    response: Response = await client.delete(
        f"/groups/{group.id}/members/{other_user_group_member.id}/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_get_group_members(
    client: AsyncClient,
    user: User,
    user_bearer_token_header: dict[str, str],
    group: Group,
) -> None:
    response: Response = await client.get(
        f"/groups/{group.id}/members/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body) == 1
    assert body[0]["user_id"] == str(user.id)
    assert body[0]["group_id"] == str(group.id)
    assert body[0]["is_owner"] is True


@pytest.mark.asyncio
async def test_get_group_member_by_id(
    client: AsyncClient,
    user: User,
    other_user_group_member: GroupMember,
    user_bearer_token_header: dict[str, str],
    group: Group,
) -> None:
    response: Response = await client.get(
        f"/groups/{group.id}/members/{other_user_group_member.id}/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["user_id"] == str(other_user_group_member.user_id)
    assert body["group_id"] == str(group.id)


@pytest.mark.asyncio
async def test_create_group_request(
    client: AsyncClient,
    user_bearer_token_header: dict[str, str],
    other_user_bearer_token_header: dict[str, str],
    group: Group,
    other_user: User,
) -> None:
    schema = CreateGroupRequestSchema(
        message="Test message",
    )
    response: Response = await client.post(
        f"/groups/{group.id}/requests/",
        headers=other_user_bearer_token_header,
        json=schema.dict(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["id"] is not None


@pytest.mark.asyncio
async def test_update_group_request(
    client: AsyncClient,
    user_bearer_token_header: dict[str, str],
    group: Group,
    other_user_group_request: GroupRequest,
) -> None:
    schema = UpdateGroupRequestSchema(
        status=GroupRequestStatus.ACCEPTED,
    )
    response: Response = await client.patch(
        f"/groups/{group.id}/requests/{other_user_group_request.id}/",
        headers=user_bearer_token_header,
        json=schema.dict(),
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == str(other_user_group_request.id)


@pytest.mark.asyncio
async def test_delete_group_request(
    client: AsyncClient,
    group: Group,
    other_user_bearer_token_header: dict[str, str],
    other_user_group_request: GroupRequest,
) -> None:
    response: Response = await client.delete(
        f"/groups/{group.id}/requests/{other_user_group_request.id}/",
        headers=other_user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_get_group_requests(
    client: AsyncClient,
    user: User,
    other_user_group_request: GroupRequest,
    user_bearer_token_header: dict[str, str],
    group: Group,
) -> None:
    response: Response = await client.get(
        f"/groups/{group.id}/requests/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body) == 1
    assert body[0]["user_id"] == str(other_user_group_request.user_id)
    assert body[0]["group_id"] == str(group.id)


@pytest.mark.asyncio
async def test_get_group_request_by_id(
    client: AsyncClient,
    user: User,
    other_user_group_request: GroupRequest,
    user_bearer_token_header: dict[str, str],
    group: Group,
) -> None:
    response: Response = await client.get(
        f"/groups/{group.id}/requests/{other_user_group_request.id}/",
        headers=user_bearer_token_header,
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["user_id"] == str(other_user_group_request.user_id)
    assert body["group_id"] == str(group.id)
