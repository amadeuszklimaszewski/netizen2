from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncConnection

from src.core.interfaces.email import EmailSender as IEmailSender
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
from src.infrastructure.email import CeleryEmailSender
from src.infrastructure.repositories.group import (
    GroupMemberRepository,
    GroupRepository,
    GroupRequestRepository,
)
from src.infrastructure.repositories.user import UserRepository

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


def get_email_sender() -> IEmailSender:
    return CeleryEmailSender()


def get_user_service(
    user_repository: IUserRepository = Depends(get_user_repository),
    email_sender: IEmailSender = Depends(get_email_sender),
) -> UserService:
    return UserService(user_repository, email_sender)


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
