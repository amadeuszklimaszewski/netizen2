from uuid import UUID

from pydantic import BaseModel

from src.core.enums.group import GroupRequestStatus
from src.core.filters.base import FilterSet


class GroupFilterSet(FilterSet):
    name__eq: str | None = None
    is_private__eq: bool | None = None


class GroupMemberFilterSet(FilterSet):
    group_id__eq: UUID | None = None
    user_id__eq: UUID | None = None
    is_admin__eq: bool | None = None
    is_owner__eq: bool | None = None


class GroupRequestFilterSet(FilterSet):
    group_id__eq: UUID | None = None
    user_id__eq: UUID | None = None
    status__eq: GroupRequestStatus | None = None


class GroupInputFilters(BaseModel):
    name__eq: str | None = None
    is_private__eq: bool | None = None


class GroupMemberInputFilters(BaseModel):
    is_admin__eq: bool | None = None
    is_owner__eq: bool | None = None
