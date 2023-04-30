from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from pydantic import BaseModel

from src.core.filters.base import FilterSet

PK = TypeVar("PK")
Model = TypeVar("Model", bound=BaseModel)


class BaseRepository(Generic[PK, Model], ABC):
    @abstractmethod
    async def get(self, pk: PK) -> Model:
        raise NotImplementedError

    @abstractmethod
    async def get_many(self, filter_set: FilterSet | None = None) -> list[Model]:
        raise NotImplementedError

    @abstractmethod
    async def persist(self, model: Model) -> None:
        raise NotImplementedError

    @abstractmethod
    async def persist_many(self, models: list[Model]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        model: Model,
        *_,
        fields_to_update: list[str] | None = None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, model: Model) -> None:
        raise NotImplementedError

    @property
    @abstractmethod
    def _model(self) -> Type[Model]:
        raise NotImplementedError
