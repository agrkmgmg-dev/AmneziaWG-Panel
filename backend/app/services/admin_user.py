"""
Admin User Service.

Provides user management for admin panel.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.repositories.user import UserRepository


class AdminUserService:
    """
    Service for admin user management.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.user_repository = UserRepository(session)

    async def get_users(self) -> list[User]:
        """
        Return all users.
        """

        return await self.user_repository.get_all()