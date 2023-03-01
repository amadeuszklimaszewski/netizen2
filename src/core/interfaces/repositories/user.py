import uuid
from abc import ABC, abstractmethod

from src.core.interfaces.repositories.base import BaseRepository
from src.core.models.user import User


class UserRepository(BaseRepository[uuid.UUID, User], ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError
