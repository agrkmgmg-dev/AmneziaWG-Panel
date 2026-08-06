from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User model.

    Contains user-specific database operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model=User)

    async def get_by_username(
        self,
        username: str,
    ) -> User | None:
        """
        Return user by username.
        """

        result = await self.session.execute(
            select(User).where(User.username == username)
        )

        return result.scalar_one_or_none()

    async def exists_username(
        self,
        username: str,
    ) -> bool:
        """
        Check whether username already exists.
        """

        result = await self.session.execute(
            select(func.count())
            .select_from(User)
            .where(User.username == username)
        )

        return result.scalar_one() > 0