from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncConnection

from src.core.interfaces.email import EmailClient as IEmailClient
from src.core.interfaces.email import EmailService as IEmailService
from src.core.interfaces.repositories.user import UserRepository as IUserRepository
from src.core.services.auth import AuthService
from src.core.services.user import UserService
from src.infrastructure.database.connection import get_db
from src.infrastructure.email import EmailService, SMTPClient
from src.infrastructure.repositories.user import UserRepository
from src.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login/")


def get_user_repository(conn: AsyncConnection = Depends(get_db)) -> IUserRepository:
    return UserRepository(conn)


def get_email_client() -> IEmailClient:
    if settings.ENVIRONMENT == "development":
        return SMTPClient()

    raise NotImplementedError


def get_email_service(
    client: IEmailClient = Depends(get_email_client),
) -> IEmailService:
    return EmailService(client)


def get_user_service(
    user_repository: IUserRepository = Depends(get_user_repository),
    email_service: IEmailService = Depends(get_email_service),
) -> UserService:
    return UserService(user_repository, email_service)


def get_auth_service(
    user_repository: IUserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repository)
