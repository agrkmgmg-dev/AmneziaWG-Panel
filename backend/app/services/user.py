"""
User service layer.

Contains business logic related to users.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.security import hash_password
from backend.app.models.user import User
from backend.app.repositories.user import UserRepository
from backend.app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
)

from backend.app.services.base import BaseService


class UserService(BaseService):
    """
    Service class for User operations.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        repository = UserRepository(session)

        super().__init__(
            session=session,
            repository=repository,
        )

        self.repository = repository

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse | None:
        user = await self.repository.get_by_id(user_id)

        if user is None:
            return None

        return UserResponse.model_validate(user)

    async def get_all(
        self,
    ) -> list[UserResponse]:
        users = await self.repository.get_all()

        return [
            UserResponse.model_validate(user)
            for user in users
        ]

    async def create(
        self,
        data: UserCreate,
    ) -> UserResponse:
        user = User(
            username=data.username,
            hashed_password=hash_password(data.password),
        )

        user = await self.repository.create(user)

        await self.commit()
        await self.refresh(user)

        return UserResponse.model_validate(user)

    async def update(
        self,
        user_id: int,
        data: UserUpdate,
    ) -> UserResponse | None:
        user = await self.repository.get_by_id(user_id)

        if user is None:
            return None

        if data.username is not None:
            username_exists = await self.repository.exists_username(
                data.username,
                exclude_user_id=user_id,
            )

            if username_exists:
                raise ValueError("Username already exists")

            user.username = data.username

        if data.password is not None:
            user.hashed_password = hash_password(
                data.password
            )

        if data.is_active is not None:
            user.is_active = data.is_active

        await self.commit()
        await self.refresh(user)

        return UserResponse.model_validate(user)

    async def delete(
        self,
        user_id: int,
    ) -> bool:
        user = await self.repository.get_by_id(user_id)

        if user is None:
            return False

        await self.repository.delete(user)

        await self.commit()

        return True
