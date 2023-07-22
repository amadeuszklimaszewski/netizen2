from uuid import UUID

from src.core.exceptions import (
    AlreadyActiveError,
    AlreadyExistsError,
    DoesNotExistError,
)
from src.core.interfaces.email import EmailService
from src.core.interfaces.repositories.user import UserRepository
from src.core.models.user import User
from src.core.schemas.email import EmailSchema
from src.core.schemas.user import CreateUserSchema, UpdateUserSchema
from src.core.utils import get_password_hash


class UserService:
    def __init__(self, repository: UserRepository, email_service: EmailService):
        self.repository = repository
        self.email_service = email_service

    async def create_user(self, schema: CreateUserSchema) -> User:
        if await self.repository.get_by_email(schema.email):
            raise AlreadyExistsError("User with given email already exists")

        hashed_password = get_password_hash(schema.password)
        user_data = schema.model_dump(exclude={"password", "repeat_password"})
        new_user = User(**user_data, password_hash=hashed_password)
        await self.repository.persist(new_user)
        return new_user

    async def send_activation_email(self, user_id: UUID) -> None:
        user = await self.repository.get(pk=user_id)

        if user.is_active:
            raise AlreadyActiveError("User is already active")

        user.generate_email_confirmation_token()
        fields_to_update = ["email_confirmation_token"]
        await self.repository.update(user, fields_to_update)

        activation_email = EmailSchema(
            subject="Thank you for registering - activate your account",
            recipients=(user.email,),
            template_name="email_confirmation.html",
            context=user.get_email_context(),
        )
        self.email_service.send_email(activation_email)

    async def send_password_reset_email(self, email: str) -> None:
        user = await self.repository.get_by_email(email)
        if not user:
            raise DoesNotExistError("User with given email does not exist")

        user.generate_password_reset_token()
        fields_to_update = ["password_reset_token", "password_reset_token_expires_at"]
        await self.repository.update(user, fields_to_update)

        password_reset_email = EmailSchema(
            subject="Password reset",
            recipients=(user.email,),
            template_name="password_reset.html",
            context=user.get_email_context(),
        )
        self.email_service.send_email(password_reset_email)

    async def activate_user(self, user_id: UUID) -> None:
        user = await self.repository.get(pk=user_id)

        user.activate()
        fields_to_update = ["is_active"]
        await self.repository.update(user, fields_to_update)

    async def confirm_email(self, user_id: UUID, confirmation_token: str) -> None:
        user = await self.repository.get(pk=user_id)

        user.confirm_email(confirmation_token)
        fields_to_update = ["is_active", "email_confirmation_token"]
        await self.repository.update(user, fields_to_update)

    async def reset_password(
        self,
        user_id: UUID,
        reset_password_token: str,
        new_password: str,
    ) -> None:
        user = await self.repository.get(pk=user_id)

        user.reset_password(reset_password_token, new_password)
        fields_to_update = [
            "password_hash",
            "password_reset_token",
            "password_reset_token_expires_at",
        ]
        await self.repository.update(user, fields_to_update)

    async def get_user(self, user_id: UUID) -> User:
        return await self.repository.get(pk=user_id)

    async def get_users(self) -> list[User]:
        # TODO: Allow filtering
        return await self.repository.get_many()

    async def delete_user(self, user: User) -> None:
        await self.repository.delete(user)

    async def update_user(self, user: User, schema: UpdateUserSchema) -> None:
        fields_to_update = []
        for key, value in schema.model_dump().items():
            setattr(user, key, value)
            fields_to_update.append(key)

        await self.repository.update(user, fields_to_update)
