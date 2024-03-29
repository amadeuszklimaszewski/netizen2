import uuid
from typing import Type

from sqlalchemy import Table, delete, select

from src.core.enums.group import GroupRequestStatus
from src.core.exceptions import DoesNotExistError
from src.core.interfaces.repositories.group import (
    GroupMemberRepository as AbstractGroupMemberRepository,
)
from src.core.interfaces.repositories.group import (
    GroupRepository as AbstractGroupRepository,
)
from src.core.interfaces.repositories.group import (
    GroupRequestRepository as AbstractGroupRequestRepository,
)
from src.core.models.group import Group, GroupMember, GroupRequest
from src.infrastructure.database.tables.group import (
    group_member_table,
    group_request_table,
    group_table,
)
from src.infrastructure.repositories.sqlalchemy import SQLAlchemyRepository


class GroupRepository(
    SQLAlchemyRepository[uuid.UUID, Group],
    AbstractGroupRepository,
):
    async def get_many_for_user(self, user_id: uuid.UUID) -> list[Group]:
        stmt = (
            select(self._table)
            .join(self._group_member_table)
            .where(self._group_member_table.c.user_id == user_id)
        )
        results = await self._conn.execute(stmt)
        return [self._model.model_validate(result) for result in results]

    @property
    def _group_member_table(self) -> Table:
        return group_member_table

    @property
    def _table(self) -> Table:
        return group_table

    @property
    def _model(self) -> Type[Group]:
        return Group


class GroupMemberRepository(
    SQLAlchemyRepository[uuid.UUID, GroupMember],
    AbstractGroupMemberRepository,
):
    async def get_by_user_and_group_id(
        self,
        user_id: uuid.UUID,
        group_id: uuid.UUID,
    ) -> GroupMember:
        stmt = (
            select(self._table)
            .where(
                self._table.c.user_id == user_id,
                self._table.c.group_id == group_id,
            )
            .limit(1)
        )
        result = (await self._conn.execute(stmt)).first()
        if not result:
            raise DoesNotExistError(
                f"{self.__class__.__name__} could not find {self._model.__name__}"
                f"with given group_id - {group_id} and user_id - {user_id}",
            )

        return self._model.model_validate(result)

    async def delete_by_group_id(self, group_id: uuid.UUID) -> None:
        stmt = delete(self._table).where(self._table.c.group_id == group_id)
        await self._conn.execute(stmt)

    @property
    def _table(self) -> Table:
        return group_member_table

    @property
    def _model(self) -> Type[GroupMember]:
        return GroupMember


class GroupRequestRepository(
    SQLAlchemyRepository[uuid.UUID, GroupRequest],
    AbstractGroupRequestRepository,
):
    async def get_pending_request_by_user_and_group_id(
        self,
        user_id: uuid.UUID,
        group_id: uuid.UUID,
    ) -> GroupRequest:
        stmt = (
            select(self._table)
            .where(
                self._table.c.user_id == user_id,
                self._table.c.group_id == group_id,
                self._table.c.status == GroupRequestStatus.PENDING,
            )
            .limit(1)
        )
        result = (await self._conn.execute(stmt)).first()
        if not result:
            raise DoesNotExistError(
                f"{self.__class__.__name__} could not find pending {self._model.__name__}"
                f"with given group_id - {group_id} and user_id - {user_id}",
            )

        return self._model.model_validate(result)

    async def delete_by_group_id(self, group_id: uuid.UUID) -> None:
        stmt = delete(self._table).where(self._table.c.group_id == group_id)
        await self._conn.execute(stmt)

    @property
    def _table(self) -> Table:
        return group_request_table

    @property
    def _model(self) -> Type[GroupRequest]:
        return GroupRequest
