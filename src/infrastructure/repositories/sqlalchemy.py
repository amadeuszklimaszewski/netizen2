from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from sqlalchemy import Table, delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection

from src.core.exceptions import AlreadyExistsError, DoesNotExistError
from src.core.interfaces.repositories.base import BaseRepository
from src.core.models.base import AppModel

PK = TypeVar("PK")
Model = TypeVar("Model", bound=AppModel)


class SQLAlchemyRepository(Generic[PK, Model], BaseRepository[PK, Model], ABC):
    def __init__(self, async_connection: AsyncConnection) -> None:
        self._conn = async_connection

    async def get(self, pk: PK) -> Model:
        stmt = select(self._table).where(self._table.c.id == pk).limit(1)
        result = (await self._conn.execute(stmt)).first()
        if not result:
            raise DoesNotExistError(
                f"{self.__class__.__name__} could not find {self._model.__name__} with given PK - {pk}",
            )
        return self._model.from_orm(result)

    async def get_many(self, **kwargs) -> list[Model]:
        args = [getattr(self._table.c, key) == val for key, val in kwargs.items()]
        stmt = select(self._table).where(*args)
        results = await self._conn.execute(stmt)
        return [self._model.from_orm(result) for result in results]

    async def persist(self, model: Model) -> None:
        stmt = insert(self._table).values(**model.dict())
        try:
            await self._conn.execute(stmt)
        except IntegrityError:
            raise AlreadyExistsError(
                f"{self.__class__.__name__} could not persist {model}: record with given PK already exists",
            )

    async def persist_many(self, models: list[Model]) -> None:
        stmt = insert(self._table).values([model.dict() for model in models])
        try:
            await self._conn.execute(stmt)
        except IntegrityError:
            raise AlreadyExistsError(
                f"{self.__class__.__name__} could not persist {models}: one or more of the models already exists",
            )

    async def update(self, model: Model) -> None:
        update_data = model.dict(exclude={"id"})
        stmt = (
            update(self._table)
            .where(self._table.c.id == model.id)
            .values(**update_data)
        )
        await self._conn.execute(stmt)

    async def delete(self, model: Model) -> None:
        stmt = delete(self._table).where(self._table.c.id == model.id)
        await self._conn.execute(stmt)

    @property
    @abstractmethod
    def _model(self) -> Type[Model]:
        raise NotImplementedError

    @property
    @abstractmethod
    def _table(self) -> Table:
        raise NotImplementedError
