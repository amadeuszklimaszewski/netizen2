from uuid import UUID

from fastapi import HTTPException, status
from fastapi.routing import APIRouter

from src.core.exceptions import (
    AlreadyActiveError,
    AlreadyExistsError,
    InvalidTokenError,
    PermissionDeniedError,
)
from src.core.schemas.user import CreateUserSchema, UpdateUserSchema
from src.web.api.v1.annotations import AccessToken, AuthService, UserService
from src.web.api.v1.schemas.base import IDOnlyOutputSchema
from src.web.api.v1.schemas.user import (
    PasswordResetSchema,
    SendPasswordResetEmailSchema,
    UserOutputSchema,
)

user_router = APIRouter(prefix="/users")


@user_router.get(
    "/",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    response_model=list[UserOutputSchema],
)
async def get_users(
    access_token: AccessToken,
    user_service: UserService,
    auth_service: AuthService,
):
    await auth_service.verify_access_token(access_token)

    return await user_service.get_users()


@user_router.post(
    "/",
    tags=["users"],
    status_code=status.HTTP_201_CREATED,
    response_model=IDOnlyOutputSchema,
)
async def create_user(
    create_user_schema: CreateUserSchema,
    user_service: UserService,
):
    try:
        user = await user_service.create_user(create_user_schema)
        await user_service.send_activation_email(user.id)
    except AlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with given email already exists",
        )
    return user


@user_router.get(
    "/profile/",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
)
async def get_current_user(
    access_token: AccessToken,
    auth_service: AuthService,
):
    return await auth_service.verify_access_token(access_token)


@user_router.post(
    "/password-reset/send-email/",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unauthenticated_send_password_reset_email(
    schema: SendPasswordResetEmailSchema,
    user_service: UserService,
):
    await user_service.send_password_reset_email(schema.email)


@user_router.get(
    "/{user_id}/",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
)
async def get_user(
    user_id: UUID,
    access_token: AccessToken,
    user_service: UserService,
    auth_service: AuthService,
):
    await auth_service.verify_access_token(access_token)

    return await user_service.get_user(user_id)


@user_router.patch(
    "/{user_id}/",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    response_model=IDOnlyOutputSchema,
)
async def update_user(
    user_id: UUID,
    schema: UpdateUserSchema,
    access_token: AccessToken,
    user_service: UserService,
    auth_service: AuthService,
):
    user = await auth_service.verify_access_token(access_token)

    if user.id != user_id and not user.is_superuser:
        raise PermissionDeniedError()

    await user_service.update_user(user, schema)
    return user


@user_router.delete(
    "/{user_id}/",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID,
    access_token: AccessToken,
    user_service: UserService,
    auth_service: AuthService,
):
    user = await auth_service.verify_access_token(access_token)

    if user.id != user_id and not user.is_superuser:
        raise PermissionDeniedError()

    await user_service.delete_user(user)


@user_router.post(
    "/{user_id}/password-reset/send-email/",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def send_password_reset_email(
    user_id: UUID,
    access_token: AccessToken,
    user_service: UserService,
    auth_service: AuthService,
):
    user = await auth_service.verify_access_token(access_token)

    if user.id != user_id and not user.is_superuser:
        raise PermissionDeniedError()

    await user_service.send_password_reset_email(user.email)


@user_router.post(
    "/{user_id}/password-reset/{token}/",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def reset_password(
    user_id: UUID,
    token: str,
    schema: PasswordResetSchema,
    user_service: UserService,
):
    try:
        await user_service.reset_password(user_id, token, schema.password)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request",
        )


@user_router.post(
    "/{user_id}/activate/send-email/",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def resend_activation_email(
    user_id: UUID,
    user_service: UserService,
):
    try:
        await user_service.send_activation_email(user_id)
    except AlreadyActiveError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request",
        )


@user_router.post(
    "/{user_id}/activate/{email_confirmation_token}/",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def confirm_email(
    user_id: UUID,
    email_confirmation_token: str,
    user_service: UserService,
):
    try:
        await user_service.confirm_email(user_id, email_confirmation_token)
    except (AlreadyActiveError, InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request",
        )
