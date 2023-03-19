import operator

import pytest

from src.core.filters import Filter, FilterSet, SQLAlchemyFilter


class TestFilterSet(FilterSet):
    field1__eq: str | None
    field2__gt: int | None
    field3__lt: int | None


@pytest.fixture
def filterset():
    return TestFilterSet(
        field1__eq="value1",
        field2__gt=2,
        field3__lt=3,
    )


def test_filter():
    filter_ = Filter(
        field="field",
        operator=operator.eq,
        value=1,
    )
    item = {"field": 1}

    assert filter_(item) is True


def test_get_filters(filterset: FilterSet):
    filters = filterset.get_filters()

    assert len(filters) == 3

    assert filters[0].field == "field1"
    assert filters[0].operator == operator.eq
    assert filters[0].value == "value1"

    assert filters[1].field == "field2"
    assert filters[1].operator == operator.gt
    assert filters[1].value == 2

    assert filters[2].field == "field3"
    assert filters[2].operator == operator.lt
    assert filters[2].value == 3


def test_get_filters_no_filters():
    filterset = FilterSet()
    filters = filterset.get_filters()

    assert not filters


def test_sqlalchemy_filter_from_filter():
    filter_ = Filter(
        field="field",
        operator=operator.eq,
        value=1,
    )
    sqlalchemy_filter = SQLAlchemyFilter.from_filter(filter_)

    assert sqlalchemy_filter.field == filter_.field
    assert sqlalchemy_filter.operator == filter_.operator
    assert sqlalchemy_filter.value == filter_.value
