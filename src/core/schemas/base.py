from typing import Any

from pydantic import BaseModel


class BaseUpdateSchema(BaseModel):
    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        kwargs.setdefault("exclude_unset", True)
        return super().model_dump(*args, **kwargs)
