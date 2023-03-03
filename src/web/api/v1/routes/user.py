from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from src.core.exceptions import (
    AlreadyActiveError,
    AlreadyExistsError,
    DoesNotExistError,
    InvalidTokenError,
)
from src.core.schemas.user import CreateUserSchema
from src.core.services.auth import AuthService
from src.core.services.user import UserService
from src.web.api.v1.dependencies import (
    get_auth_service,
    get_user_service,
    oauth2_scheme,
)
from src.web.api.v1.schemas.base import IDOnlyOutputSchema
from src.web.api.v1.schemas.user import UserOutputSchema

user_router = APIRouter(prefix="/users")


@user_router.get(
    "/",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    response_model=list[UserOutputSchema],
)
async def get_users(
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_users()


@user_router.post(
    "/",
    tags=["users"],
    status_code=status.HTTP_201_CREATED,
    response_model=IDOnlyOutputSchema,
)
async def create_user(
    create_user_schema: CreateUserSchema,
    user_service: UserService = Depends(get_user_service),
):
    try:
        user = await user_service.create_user(create_user_schema)
        await user_service.send_activation_email(user.id)
    except AlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with given email already exists",
        )
    return user.id


@user_router.get(
    "/profile/",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
)
async def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = await auth_service.verify_access_token(access_token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    return user


@user_router.post(
    "/password-reset/",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unauthenticated_send_password_reset_email(
    email: str,
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.send_password_reset_email(email)
    except DoesNotExistError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )


@user_router.get(
    "/{user_id}/",
    tags=["users"],
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user(user_id)


@user_router.post(
    "/{user_id}/password-reset/",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def send_password_reset_email(
    user_id: UUID,
    access_token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.verify_access_token(access_token)

    if user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )

    await user_service.send_password_reset_email(user.email)


@user_router.post(
    "/{user_id}/password-reset/{token}",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def reset_password(
    user_id: UUID,
    token: str,
    new_password: str,
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.reset_password(user_id, token, new_password)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )


@user_router.post(
    "/{user_id}/activate/",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def resend_activation_email(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.send_activation_email(user_id)
    except AlreadyActiveError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request",
        )


@user_router.post(
    "/{user_id}/activate/{email_confirmation_token}",
    tags=["users"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def confirm_email(
    user_id: UUID,
    email_confirmation_token: str,
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.confirm_email(user_id, email_confirmation_token)
    except AlreadyActiveError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request",
        )
