from typing import Any

from pydantic import BaseModel


class BaseUpdateSchema(BaseModel):
    def dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        kwargs.setdefault("exclude_unset", True)
        return super().dict(*args, **kwargs)
