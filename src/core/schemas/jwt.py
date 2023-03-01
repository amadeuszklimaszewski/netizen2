from uuid import UUID

from pydantic import BaseModel, Field

from src.core.utils import get_jwt_expire_time


class JWTPayload(BaseModel):
    sub: UUID
    exp: int = Field(default_factory=get_jwt_expire_time)
