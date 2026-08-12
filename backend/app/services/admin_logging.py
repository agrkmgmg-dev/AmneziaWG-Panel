from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.activity_log import ActivityLogCreate
from backend.app.services.activity_log import ActivityLogService


async def log_admin_action(
    session: AsyncSession,
    action: str,
    description: str | None = None,
) -> None:
    service = ActivityLogService(session)

    await service.create(
        ActivityLogCreate(
            user_id=None,
            action=action,
            description=description,
        )
    )
