from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class IDOnlyOutputSchema(BaseModel):
    id: UUID


class BaseOutputSchema(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
