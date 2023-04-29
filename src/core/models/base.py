from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AppModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True
