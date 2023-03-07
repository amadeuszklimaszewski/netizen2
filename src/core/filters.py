import operator
from typing import Callable

from pydantic import BaseModel
from sqlalchemy import Table


class Filter(BaseModel):
    field: str
    operator: Callable
    value: str

    def __call__(self, item):
        return self.operator(item[self.field], self.value)


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
        for key, value in self.dict(exclude_none=True).items():
            field, operator_ = key.split("__")
            filters.append(
                Filter(
                    field=field,
                    operator=self._get_operator(operator_),
                    value=value,
                ),
            )

        return filters

    @classmethod
    def _get_operator(cls, operator_name: str) -> Callable:
        return cls._operators_mapping[operator_name]
