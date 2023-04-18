from src.core.exceptions import (
    DoesNotExistError,
    InvalidCredentialsError,
    UserNotActiveError,
)
from src.core.interfaces.repositories.user import UserRepository
from src.core.models.user import User
from src.core.schemas.auth import AccessToken, UserCredentials
from src.core.schemas.jwt import JWTPayload
from src.core.services.jwt import decode_jwt, encode_jwt
from src.core.utils import verify_password


class AuthService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def create_access_token(self, user: User) -> str:
        payload = JWTPayload(sub=user.id)
        return encode_jwt(payload)

    async def verify_access_token(self, auth_token: str) -> User:
        payload = decode_jwt(auth_token)
        try:
            user = await self.repository.get(payload.sub)
        except DoesNotExistError:
            raise InvalidCredentialsError("Invalid credentials")

        if not user.is_active:
            raise UserNotActiveError("Please activate your account")

        return user

    async def authenticate_user(self, credentials: UserCredentials) -> AccessToken:
        user = await self.repository.get_by_email(credentials.email)

        if not user or not verify_password(credentials.password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")

        if not user.is_active:
            raise UserNotActiveError("Please activate your account")

        token = self.create_access_token(user)
        return AccessToken(access_token=token, token_type="bearer")
