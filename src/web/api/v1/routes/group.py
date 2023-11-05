from typing import Annotated
from uuid import UUID

from fastapi import Depends, status
from fastapi.routing import APIRouter

from src.core.filters.group import GroupInputFilters, GroupMemberInputFilters
from src.core.schemas.group import (
    CreateGroupRequestSchema,
    CreateGroupSchema,
    UpdateGroupMemberSchema,
    UpdateGroupRequestSchema,
    UpdateGroupSchema,
)
from src.web.api.v1.annotations import GroupService, User
from src.web.api.v1.schemas.base import IDOnlyOutputSchema
from src.web.api.v1.schemas.group import (
    GroupMemberOutputSchema,
    GroupOutputSchema,
    GroupRequestOutputSchema,
)

group_router = APIRouter(prefix="/groups")


@group_router.get(
    "/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupOutputSchema],
)
async def get_groups(
    request_user: User,
    group_service: GroupService,
    filters: Annotated[GroupInputFilters, Depends()],
):
    return await group_service.get_groups(filters)


@group_router.post(
    "/",
    tags=["groups"],
    status_code=status.HTTP_201_CREATED,
    response_model=IDOnlyOutputSchema,
)
async def create_group(
    schema: CreateGroupSchema,
    request_user: User,
    group_service: GroupService,
):
    return await group_service.create_group(request_user.id, schema)


@group_router.get(
    "/user/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupOutputSchema],
)
async def get_groups_for_user(
    request_user: User,
    group_service: GroupService,
):
    return await group_service.get_groups_for_user(request_user.id)


@group_router.get(
    "/user/requests/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupRequestOutputSchema],
)
async def get_group_requests_for_user(
    request_user: User,
    group_service: GroupService,
):
    return await group_service.get_group_requests_for_user(request_user.id)


@group_router.get(
    "/{group_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=GroupOutputSchema,
)
async def get_group(
    group_id: UUID,
    request_user: User,
    group_service: GroupService,
):
    return await group_service.get_group(group_id)


@group_router.patch(
    "/{group_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=IDOnlyOutputSchema,
)
async def update_group(
    group_id: UUID,
    schema: UpdateGroupSchema,
    request_user: User,
    group_service: GroupService,
):
    await group_service.update_group(request_user.id, group_id, schema)
    return IDOnlyOutputSchema(id=group_id)


@group_router.delete(
    "/{group_id}/",
    tags=["groups"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_group(
    group_id: UUID,
    request_user: User,
    group_service: GroupService,
):
    await group_service.delete_group(request_user.id, group_id)


@group_router.get(
    "/{group_id}/members/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupMemberOutputSchema],
)
async def get_group_members(
    group_id: UUID,
    request_user: User,
    group_service: GroupService,
    filters: Annotated[GroupMemberInputFilters, Depends()],
):
    return await group_service.get_group_members(request_user.id, group_id, filters)


@group_router.get(
    "/{group_id}/members/{member_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=GroupMemberOutputSchema,
)
async def get_group_member(
    group_id: UUID,
    member_id: UUID,
    request_user: User,
    group_service: GroupService,
):
    return await group_service.get_group_member(request_user.id, group_id, member_id)


@group_router.patch(
    "/{group_id}/members/{member_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=IDOnlyOutputSchema,
)
async def update_group_member(
    group_id: UUID,
    member_id: UUID,
    schema: UpdateGroupMemberSchema,
    request_user: User,
    group_service: GroupService,
):
    await group_service.update_group_member(
        request_user.id,
        group_id,
        member_id,
        schema,
    )
    return IDOnlyOutputSchema(id=member_id)


@group_router.delete(
    "/{group_id}/members/{member_id}/",
    tags=["groups"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_group_member(
    group_id: UUID,
    member_id: UUID,
    request_user: User,
    group_service: GroupService,
):
    await group_service.delete_group_member(request_user.id, group_id, member_id)


@group_router.get(
    "/{group_id}/requests/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupRequestOutputSchema],
)
async def get_group_requests_for_group(
    group_id: UUID,
    request_user: User,
    group_service: GroupService,
):
    return await group_service.get_group_requests_for_group(request_user.id, group_id)


@group_router.post(
    "/{group_id}/requests/",
    tags=["groups"],
    status_code=status.HTTP_201_CREATED,
    response_model=IDOnlyOutputSchema,
)
async def create_group_request(
    group_id: UUID,
    schema: CreateGroupRequestSchema,
    request_user: User,
    group_service: GroupService,
):
    return await group_service.create_group_request(request_user.id, group_id, schema)


@group_router.get(
    "/{group_id}/requests/{request_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=GroupRequestOutputSchema,
)
async def get_group_request(
    group_id: UUID,
    request_id: UUID,
    request_user: User,
    group_service: GroupService,
):
    return await group_service.get_group_request(request_user.id, group_id, request_id)


@group_router.patch(
    "/{group_id}/requests/{request_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=IDOnlyOutputSchema,
)
async def update_group_request(
    group_id: UUID,
    request_id: UUID,
    schema: UpdateGroupRequestSchema,
    request_user: User,
    group_service: GroupService,
):
    await group_service.update_group_request(
        request_user.id,
        group_id,
        request_id,
        schema,
    )
    return IDOnlyOutputSchema(id=request_id)


@group_router.delete(
    "/{group_id}/requests/{request_id}/",
    tags=["groups"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_group_request(
    group_id: UUID,
    request_id: UUID,
    request_user: User,
    group_service: GroupService,
):
    await group_service.delete_group_request(request_user.id, group_id, request_id)
