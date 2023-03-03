from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserOutputSchema(BaseModel):
    id: UUID
    email: str
    is_active: bool

    first_name: str | None
    last_name: str | None
    date_of_birth: datetime | None
