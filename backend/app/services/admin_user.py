"""
Admin user service.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.repositories.user import UserRepository
from backend.app.core.security import hash_password


class AdminUserService:
    """
    Service for admin user management.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        self.user_repository = UserRepository(
            session
        )


    async def get_users(
        self,
    ) -> list[User]:
        """
        Return all users.
        """

        return await self.user_repository.get_all()


    async def get_user(
        self,
        user_id: int,
    ) -> User | None:
        """
        Return one user.
        """

        return await self.user_repository.get_by_id(
            user_id
        )


    async def create_user(
        self,
        username: str,
        password: str,
    ) -> User | None:
        """
        Create new user.
        """

        existing_user = await self.user_repository.get_by_username(
            username
        )

        if existing_user:
            return None


        user = User(
            username=username,
            hashed_password=hash_password(password),
            is_active=True,
        )

        return await self.user_repository.create(
            user
        )


    async def delete_user(
        self,
        user_id: int,
    ) -> bool:
        """
        Delete user by ID.
        """

        user = await self.user_repository.get_by_id(
            user_id
        )

        if not user:
            return False

        await self.user_repository.delete(
            user
        )

        return True