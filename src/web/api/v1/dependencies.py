from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncConnection

from src.core.interfaces.email import EmailClient as IEmailClient
from src.core.interfaces.email import EmailService as IEmailService
from src.core.interfaces.repositories.group import (
    GroupMemberRepository as IGroupMemberRepository,
)
from src.core.interfaces.repositories.group import GroupRepository as IGroupRepository
from src.core.interfaces.repositories.group import (
    GroupRequestRepository as IGroupRequestRepository,
)
from src.core.interfaces.repositories.user import UserRepository as IUserRepository
from src.core.services.auth import AuthService
from src.core.services.group import GroupService
from src.core.services.user import UserService
from src.infrastructure.database.connection import get_db
from src.infrastructure.email import EmailService, SMTPClient
from src.infrastructure.repositories.group import (
    GroupMemberRepository,
    GroupRepository,
    GroupRequestRepository,
)
from src.infrastructure.repositories.user import UserRepository
from src.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login/")


def get_user_repository(
    conn: AsyncConnection = Depends(get_db),
) -> IUserRepository:
    return UserRepository(conn)


def get_group_repository(
    conn: AsyncConnection = Depends(get_db),
) -> IGroupRepository:
    return GroupRepository(conn)


def get_group_member_repository(
    conn: AsyncConnection = Depends(get_db),
) -> IGroupMemberRepository:
    return GroupMemberRepository(conn)


def get_group_request_repository(
    conn: AsyncConnection = Depends(get_db),
) -> IGroupRequestRepository:
    return GroupRequestRepository(conn)


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


def get_group_service(
    group_repository: IGroupRepository = Depends(get_group_repository),
    group_member_repository: IGroupMemberRepository = Depends(
        get_group_member_repository,
    ),
    group_request_repository: IGroupRequestRepository = Depends(
        get_group_request_repository,
    ),
) -> GroupService:
    return GroupService(
        group_repository,
        group_member_repository,
        group_request_repository,
    )
