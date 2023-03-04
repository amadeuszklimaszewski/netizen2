from src.core.exceptions import (
    DoesNotExistError,
    InvalidCredentialsError,
    UserNotActiveError,
)
from src.core.interfaces.repositories.user import UserRepository
from src.core.models.user import User
from src.core.schemas.auth import UserCredentials
from src.core.schemas.jwt import JWTPayload
from src.core.services.jwt import decode_jwt, encode_jwt
from src.core.utils import verify_password


class AuthService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def create_access_token(self, user: User) -> str:
        payload = JWTPayload(sub=user.id)
        return encode_jwt(payload)

    async def verify_access_token(self, auth_token) -> User:
        payload = decode_jwt(auth_token)
        try:
            user = await self.repository.get(payload.sub)
        except DoesNotExistError:
            raise InvalidCredentialsError("Invalid credentials")

        if not user.is_active:
            raise UserNotActiveError("Please activate your account")

        return user

    async def verify_user_credentials(self, credentials: UserCredentials) -> str:
        try:
            user = await self.repository.get_by_email(credentials.email)
        except DoesNotExistError:
            raise InvalidCredentialsError("Invalid credentials")

        if not user or not verify_password(credentials.password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")

        return self.create_access_token(user)
