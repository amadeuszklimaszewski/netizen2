from uuid import UUID

from pydantic import BaseModel, Field

from src.constants import constants
from src.core.enums.group import GroupRequestStatus
from src.core.schemas.base import BaseUpdateSchema


class CreateGroupSchema(BaseModel):
    owner_id: UUID
    is_private: bool = False

    name: str = Field(max_length=constants.MAX_GROUP_NAME_LENGTH)
    description: str | None = Field(
        default=None,
        max_length=constants.MAX_GROUP_DESCRIPTION_LENGTH,
    )


class UpdateGroupSchema(BaseUpdateSchema):
    owner_id: bool | None
    is_private: bool | None

    name: str | None = Field(max_length=constants.MAX_GROUP_NAME_LENGTH)
    description: str | None = Field(max_length=constants.MAX_GROUP_DESCRIPTION_LENGTH)


class CreateGroupRequestSchema(BaseModel):
    user_id: UUID
    group_id: UUID
    message: str | None = Field(
        default=None,
        max_length=constants.MAX_GROUP_REQUEST_MESSAGE_LENGTH,
    )


class UpdateGroupRequestSchema(BaseUpdateSchema):
    status: GroupRequestStatus


class CreateGroupMemberSchema(BaseModel):
    user_id: UUID
    group_id: UUID
    is_admin: bool


class UpdateGroupMemberSchema(BaseUpdateSchema):
    is_admin: bool | None
