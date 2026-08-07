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
)

from backend.app.services.base import BaseService


class UserService(BaseService):
    """
    Service class for User operations.

    Responsibilities:
        - Handle user business logic.
        - Manage transactions.
        - Hash passwords before persistence.
        - Coordinate with UserRepository.

    Authentication and authorization logic
    are intentionally not handled here.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        Initialize UserService.

        Args:
            session:
                Async SQLAlchemy database session.
        """

        repository = UserRepository(
            session
        )

        super().__init__(
            session=session,
            repository=repository,
        )

        self.repository = repository


    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse | None:
        """
        Get user by ID.
        """

        user = await self.repository.get_by_id(
            user_id
        )

        if user is None:
            return None

        return UserResponse.model_validate(
            user
        )


    async def get_all(
        self,
    ) -> list[UserResponse]:
        """
        Get all users.
        """

        users = await self.repository.get_all()

        return [
            UserResponse.model_validate(user)
            for user in users
        ]


    async def create(
        self,
        data: UserCreate,
    ) -> UserResponse:
        """
        Create new user.

        Password is hashed before storing.
        """

        user = User(
            username=data.username,
            hashed_password=hash_password(
                data.password
            ),
        )

        user = await self.repository.create(
            user
        )

        await self.commit()

        await self.refresh(
            user
        )

        return UserResponse.model_validate(
            user
        )


    async def delete(
        self,
        user_id: int,
    ) -> bool:
        """
        Delete user by ID.
        """

        user = await self.repository.get_by_id(
            user_id
        )

        if user is None:
            return False

        await self.repository.delete(
            user
        )

        await self.commit()

        return True