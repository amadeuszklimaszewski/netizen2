from uuid import UUID

from tests.fakes.database import FakeDatabase

from src.core.exceptions import AlreadyExistsError, DoesNotExistError
from src.core.filters.base import FilterSet
from src.core.interfaces.repositories.user import UserRepository
from src.core.models.user import User


class FakeUserRepository(UserRepository):
    def __init__(self, db: FakeDatabase) -> None:
        self.db = db

    async def get(self, pk: UUID) -> User:
        try:
            return self.db.users[pk]
        except KeyError:
            raise DoesNotExistError("User does not exist")

    async def get_by_email(self, email: str) -> User | None:
        for user in self.db.users.values():
            if user.email == email:
                return user

        return None

    async def get_many(self, filter_set: FilterSet | None = None) -> list[User]:
        return list(self.db.users.values())

    async def persist(self, user: User) -> None:
        if user.id in self.db.users:
            raise AlreadyExistsError("User already exists")
        self.db.users[user.id] = user

    async def persist_many(self, users: list[User]) -> None:
        for user in users:
            if user.id in self.db.users:
                raise AlreadyExistsError("User already exists")
            self.db.users[user.id] = user

    async def update(
        self,
        user: User,
        *_,
        fields_to_update: list[str] | None = None,
    ) -> None:
        self.db.users[user.id] = user

    async def delete(self, user: User) -> None:
        del self.db.users[user.id]

    @property
    def _model(self) -> type[User]:
        return User
