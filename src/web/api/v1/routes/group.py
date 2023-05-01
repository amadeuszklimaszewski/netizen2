from typing import Annotated
from uuid import UUID

from fastapi import Depends, status
from fastapi.routing import APIRouter

from src.core.filters.group import (
    GroupInputFilters,
    GroupMemberInputFilters,
    GroupRequestInputFilters,
)
from src.core.schemas.group import (
    CreateGroupRequestSchema,
    CreateGroupSchema,
    UpdateGroupMemberSchema,
    UpdateGroupRequestSchema,
    UpdateGroupSchema,
)
from src.web.api.v1.annotations import AccessToken, AuthService, GroupService
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
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
    filters: Annotated[GroupInputFilters, Depends()],
):
    await auth_service.verify_access_token(access_token)

    return await group_service.get_groups(filters)


@group_router.post(
    "/",
    tags=["groups"],
    status_code=status.HTTP_201_CREATED,
    response_model=IDOnlyOutputSchema,
)
async def create_group(
    schema: CreateGroupSchema,
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
):
    user = await auth_service.verify_access_token(access_token)

    return await group_service.create_group(user.id, schema)


@group_router.get(
    "/{group_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=GroupOutputSchema,
)
async def get_group(
    group_id: UUID,
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
):
    await auth_service.verify_access_token(access_token)

    return await group_service.get_group(group_id)


@group_router.put(
    "/{group_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=IDOnlyOutputSchema,
)
async def update_group(
    group_id: UUID,
    schema: UpdateGroupSchema,
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
):
    user = await auth_service.verify_access_token(access_token)

    await group_service.update_group(user.id, group_id, schema)
    return IDOnlyOutputSchema(id=group_id)


@group_router.delete(
    "/{group_id}/",
    tags=["groups"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_group(
    group_id: UUID,
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
):
    user = await auth_service.verify_access_token(access_token)

    await group_service.delete_group(user.id, group_id)


@group_router.get(
    "/{group_id}/members/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupMemberOutputSchema],
)
async def get_group_members(
    group_id: UUID,
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
    filters: Annotated[GroupMemberInputFilters, Depends()],
):
    user = await auth_service.verify_access_token(access_token)

    return await group_service.get_group_members(user.id, group_id, filters)


@group_router.get(
    "/{group_id}/members/{member_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=GroupMemberOutputSchema,
)
async def get_group_member(
    group_id: UUID,
    member_id: UUID,
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
):
    user = await auth_service.verify_access_token(access_token)

    return await group_service.get_group_member(user.id, group_id, member_id)


@group_router.put(
    "/{group_id}/members/{member_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=IDOnlyOutputSchema,
)
async def update_group_member(
    group_id: UUID,
    member_id: UUID,
    schema: UpdateGroupMemberSchema,
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
):
    user = await auth_service.verify_access_token(access_token)

    await group_service.update_group_member(user.id, group_id, member_id, schema)
    return IDOnlyOutputSchema(id=member_id)


@group_router.delete(
    "/{group_id}/members/{member_id}/",
    tags=["groups"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_group_member(
    group_id: UUID,
    member_id: UUID,
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
):
    user = await auth_service.verify_access_token(access_token)

    await group_service.delete_group_member(user.id, group_id, member_id)


@group_router.get(
    "/{group_id}/requests/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=list[GroupRequestOutputSchema],
)
async def get_group_requests(
    group_id: UUID,
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
    filters: Annotated[GroupRequestInputFilters, Depends()],
):
    user = await auth_service.verify_access_token(access_token)

    return await group_service.get_group_requests(user.id, group_id, filters)


@group_router.post(
    "/{group_id}/requests/",
    tags=["groups"],
    status_code=status.HTTP_201_CREATED,
    response_model=IDOnlyOutputSchema,
)
async def create_group_request(
    group_id: UUID,
    schema: CreateGroupRequestSchema,
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
):
    user = await auth_service.verify_access_token(access_token)

    return await group_service.create_group_request(user.id, group_id, schema)


@group_router.get(
    "/{group_id}/requests/{request_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=GroupRequestOutputSchema,
)
async def get_group_request(
    group_id: UUID,
    request_id: UUID,
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
):
    user = await auth_service.verify_access_token(access_token)

    return await group_service.get_group_request(user.id, group_id, request_id)


@group_router.put(
    "/{group_id}/requests/{request_id}/",
    tags=["groups"],
    status_code=status.HTTP_200_OK,
    response_model=IDOnlyOutputSchema,
)
async def update_group_request(
    group_id: UUID,
    request_id: UUID,
    schema: UpdateGroupRequestSchema,
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
):
    user = await auth_service.verify_access_token(access_token)

    await group_service.update_group_request(user.id, group_id, request_id, schema)
    return IDOnlyOutputSchema(id=request_id)


@group_router.delete(
    "/{group_id}/requests/{request_id}/",
    tags=["groups"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_group_request(
    group_id: UUID,
    request_id: UUID,
    access_token: AccessToken,
    group_service: GroupService,
    auth_service: AuthService,
):
    user = await auth_service.verify_access_token(access_token)

    await group_service.delete_group_request(user.id, group_id, request_id)
