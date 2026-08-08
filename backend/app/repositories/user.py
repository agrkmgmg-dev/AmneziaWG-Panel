from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User model.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session=session,
            model=User,
        )

    async def get_all(self) -> list[User]:
        """
        Return all users ordered by ID.
        """

        result = await self.session.execute(
            select(User).order_by(User.id)
        )

        return list(result.scalars().all())

    async def get_by_username(
        self,
        username: str,
    ) -> User | None:
        """
        Return user by username.
        """

        result = await self.session.execute(
            select(User).where(
                User.username == username
            )
        )

        return result.scalar_one_or_none()

    async def exists_username(
        self,
        username: str,
        exclude_user_id: int | None = None,
    ) -> bool:
        """
        Check whether username already exists.

        When exclude_user_id is provided, that user is
        excluded from the uniqueness check.
        """

        query = (
            select(func.count())
            .select_from(User)
            .where(User.username == username)
        )

        if exclude_user_id is not None:
            query = query.where(
                User.id != exclude_user_id
            )

        result = await self.session.execute(query)

        return result.scalar_one() > 0

    async def count(self) -> int:
        """
        Count total users.
        """

        result = await self.session.execute(
            select(func.count())
            .select_from(User)
        )

        return result.scalar_one()
