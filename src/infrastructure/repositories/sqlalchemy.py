from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from sqlalchemy import CursorResult, Table, delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection

from src.core.exceptions import AlreadyExistsError, DoesNotExistError
from src.core.filters import FilterSet, SQLAlchemyFilter
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

    async def get_many(self, filter_set: FilterSet | None = None) -> list[Model]:
        exps = []
        if filter_set:
            sa_filters = [
                SQLAlchemyFilter.from_filter(filter_)
                for filter_ in filter_set.get_filters()
            ]
            exps = [filter_(self._table) for filter_ in sa_filters]

        stmt = select(self._table).where(*exps)
        results: CursorResult = await self._conn.execute(stmt)
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

    async def update(
        self,
        model: Model,
        *_,
        fields_to_update: list[str] | None = None,
    ) -> None:
        """
        Update a row in the corresponding table for the given model.

        :param model: The model instance to update in the database.
        :param fields_to_update: An optional list of field names to update.
            If specified, only the given fields will be updated in the database.
            If not specified, all fields except for 'id', 'created_at', and 'updated_at'
            will be updated in the database.

        Note: This method ignores the 'created_at' and 'updated_at' fields as these fields are
        automatically set by the database.
        """
        if fields_to_update:
            update_data = {
                field: getattr(model, field)
                for field in fields_to_update
                if field not in {"created_at", "updated_at"}
            }
        else:
            update_data = model.dict(exclude={"id", "created_at", "updated_at"})

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
