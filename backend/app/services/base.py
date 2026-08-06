"""
Base Service.

Provides common functionality for all service classes.
"""

from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """
    Generic async service base.

    Responsible for business layer orchestration and
    transaction management.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: BaseRepository[ModelType],
    ) -> None:
        """
        Initialize service.

        Args:
            session: Async SQLAlchemy session.
            repository: Repository instance.
        """
        self.session = session
        self.repository = repository

    async def commit(self) -> None:
        """
        Commit current transaction.
        """
        await self.session.commit()

    async def rollback(self) -> None:
        """
        Roll back current transaction.
        """
        await self.session.rollback()

    async def refresh(
        self,
        obj: ModelType,
    ) -> None:
        """
        Refresh ORM object from database.
        """
        await self.session.refresh(obj)