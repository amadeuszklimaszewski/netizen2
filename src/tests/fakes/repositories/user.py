from uuid import UUID

from src.core.exceptions import AlreadyExistsError, DoesNotExistError
from src.core.interfaces.repositories.user import UserRepository
from src.core.models.user import User


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self.users: dict[UUID, User] = {}

    async def get(self, pk: UUID) -> User:
        try:
            return self.users[pk]
        except KeyError:
            raise DoesNotExistError("User does not exist")

    async def get_by_email(self, email: str) -> User | None:
        for user in self.users.values():
            if user.email == email:
                return user

        return None

    async def get_many(self, **kwargs) -> list[User]:
        return list(self.users.values())

    async def persist(self, user: User) -> None:
        if user.id in self.users:
            raise AlreadyExistsError("User already exists")
        self.users[user.id] = user

    async def persist_many(self, users: list[User]) -> None:
        for user in users:
            if user.id in self.users:
                raise AlreadyExistsError("User already exists")
            self.users[user.id] = user

    async def update(
        self,
        user: User,
        *_,
        fields_to_update: list[str] | None = None,
    ) -> None:
        self.users[user.id] = user

    async def delete(self, user: User) -> None:
        del self.users[user.id]

    @property
    def _model(self) -> type[User]:
        return User
