from typing import Annotated

from fastapi import Depends

from src.core.services.auth import AuthService as _AuthService
from src.core.services.group import GroupService as _GroupService
from src.core.services.user import UserService as _UserService
from src.web.api.v1.dependencies import (
    get_auth_service,
    get_group_service,
    get_user_service,
    oauth2_scheme,
)

AccessToken = Annotated[str, Depends(oauth2_scheme)]
UserService = Annotated[_UserService, Depends(get_user_service)]
AuthService = Annotated[_AuthService, Depends(get_auth_service)]
GroupService = Annotated[_GroupService, Depends(get_group_service)]
