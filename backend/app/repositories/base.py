from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Generic async repository base.

    Provides common database operations
    for all repositories.
    """

    def __init__(
        self,
        session: AsyncSession,
        model: type[ModelType],
    ) -> None:

        self.session = session
        self.model = model


    async def get_by_id(
        self,
        object_id: int,
    ) -> ModelType | None:
        """
        Retrieve object by primary key.
        """

        result = await self.session.execute(
            select(self.model).where(
                self.model.id == object_id
            )
        )

        return result.scalar_one_or_none()


    async def get_all(
        self,
    ) -> list[ModelType]:
        """
        Retrieve all objects.
        """

        result = await self.session.execute(
            select(self.model)
        )

        return list(result.scalars().all())


    async def count(
        self,
    ) -> int:
        """
        Return total records count.
        """

        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )

        return result.scalar_one()


    async def create(
        self,
        obj: ModelType,
    ) -> ModelType:
        """
        Add new object.
        """

        self.session.add(obj)

        await self.session.commit()

        await self.session.refresh(obj)

        return obj


    async def delete(
        self,
        obj: ModelType,
    ) -> None:
        """
        Delete object.
        """

        await self.session.delete(obj)

        await self.session.commit()