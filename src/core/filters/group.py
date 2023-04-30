from uuid import UUID

from pydantic import BaseModel

from src.core.enums.group import GroupRequestStatus
from src.core.filters.base import FilterSet


class GroupFilterSet(FilterSet):
    name__eq: str | None
    is_private__eq: bool | None


class GroupMemberFilterSet(FilterSet):
    group_id__eq: UUID | None
    user_id__eq: UUID | None
    is_admin__eq: bool | None
    is_owner__eq: bool | None


class GroupRequestFilterSet(FilterSet):
    group_id__eq: UUID | None
    user_id__eq: UUID | None
    status__eq: GroupRequestStatus | None


class GroupInputFilters(BaseModel):
    name__eq: str | None = None
    is_private__eq: bool | None = None


class GroupMemberInputFilters(BaseModel):
    is_admin__eq: bool | None = None
    is_owner__eq: bool | None = None


class GroupRequestInputFilters(BaseModel):
    status__eq: GroupRequestStatus | None = None
