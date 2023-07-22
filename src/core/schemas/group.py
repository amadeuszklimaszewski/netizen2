from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.constants import constants
from src.core.enums.group import GroupRequestStatus
from src.core.schemas.base import BaseUpdateSchema


class CreateGroupSchema(BaseModel):
    name: str = Field(max_length=constants.MAX_GROUP_NAME_LENGTH)
    description: str | None = Field(
        default=None,
        max_length=constants.MAX_GROUP_DESCRIPTION_LENGTH,
    )
    is_private: bool = False


class UpdateGroupSchema(BaseUpdateSchema):
    name: str | None = Field(default=None, max_length=constants.MAX_GROUP_NAME_LENGTH)
    description: str | None = Field(
        default=None,
        max_length=constants.MAX_GROUP_DESCRIPTION_LENGTH,
    )
    is_private: bool | None = None


class CreateGroupRequestSchema(BaseModel):
    message: str | None = Field(
        default=None,
        max_length=constants.MAX_GROUP_REQUEST_MESSAGE_LENGTH,
    )


class UpdateGroupRequestSchema(BaseUpdateSchema):
    status: GroupRequestStatus

    @field_validator("status")
    @classmethod
    def validate_status(cls, status: GroupRequestStatus) -> GroupRequestStatus:
        if status == GroupRequestStatus.PENDING:
            raise ValueError("Can only update status to APPROVED or REJECTED")
        return status


class CreateGroupMemberSchema(BaseModel):
    user_id: UUID
    group_id: UUID
    is_admin: bool = False
    is_owner: bool = False


class UpdateGroupMemberSchema(BaseUpdateSchema):
    is_admin: bool
