from uuid import UUID

from pydantic import BaseModel


class IDOnlyOutputSchema(BaseModel):
    id: UUID
