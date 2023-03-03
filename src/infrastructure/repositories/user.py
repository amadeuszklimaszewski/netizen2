import uuid
from typing import Type

from sqlalchemy import Table, select

from src.core.exceptions import DoesNotExistError
from src.core.interfaces.repositories.user import (
    UserRepository as AbstractUserRepository,
)
from src.core.models.user import User
from src.infrastructure.database.tables.user import user_table
from src.infrastructure.repositories.sqlalchemy import SQLAlchemyRepository


class UserRepository(
    SQLAlchemyRepository[uuid.UUID, User],
    AbstractUserRepository,
):
    async def get_by_email(self, email: str) -> User | None:
        stmt = select(self._table).where(self._table.c.email == email).limit(1)
        result = (await self._conn.execute(stmt)).first()
        if not result:
            raise DoesNotExistError("User does not exist")

        return self._model.from_orm(result)

    @property
    def _table(self) -> Table:
        return user_table

    @property
    def _model(self) -> Type[User]:
        return User
