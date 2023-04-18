from fastapi import Depends, status
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from src.core.schemas.auth import AccessToken, UserCredentials
from src.core.services.auth import AuthService
from src.web.api.v1.dependencies import get_auth_service

auth_router = APIRouter(prefix="/auth")


@auth_router.post(
    "/login/",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
    response_model=AccessToken,
)
async def authenticate_user(
    credentials: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    user_credentials = UserCredentials(
        email=credentials.username,
        password=credentials.password,
    )
    return await auth_service.authenticate_user(user_credentials)
