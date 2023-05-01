import operator
from typing import Callable
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Table


class Filter(BaseModel):
    field: str
    operator: Callable
    value: UUID | int | float | bool | str

    def __call__(self, item):
        return self.operator(getattr(item, self.field), self.value)


class SQLAlchemyFilter(Filter):
    def __call__(self, table: Table):
        column = getattr(table.c, self.field)
        return self.operator(column, self.value)

    @classmethod
    def from_filter(cls, filter_: Filter) -> "SQLAlchemyFilter":
        return cls(
            field=filter_.field,
            operator=filter_.operator,
            value=filter_.value,
        )


class FilterSet(BaseModel):
    _operators_mapping = {
        "eq": operator.eq,
        "ne": operator.ne,
        "lt": operator.lt,
        "le": operator.le,
        "gt": operator.gt,
        "ge": operator.ge,
    }

    def get_filters(self) -> list[Filter]:
        filters = []
        for key, value in self.dict(exclude_none=True, exclude_unset=True).items():
            field, operator_ = key.split("__")
            try:
                operator_func = self._get_operator(operator_)
            except KeyError:
                raise ValueError(f"Invalid operator: {operator_}")

            filters.append(
                Filter(
                    field=field,
                    operator=operator_func,
                    value=value,
                ),
            )

        return filters

    @classmethod
    def _get_operator(cls, operator_name: str) -> Callable:
        return cls._operators_mapping[operator_name]
