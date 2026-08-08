"""
Activity Logs API router.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from backend.app.api.dependencies import get_activity_log_service
from backend.app.core.dependencies import require_active_user
from backend.app.models.user import User
from backend.app.schemas.activity_log import (
    ActivityLogCreate,
    ActivityLogResponse,
)
from backend.app.services.activity_log import ActivityLogService


router = APIRouter(
    prefix="/activity-logs",
    tags=["Activity Logs"],
)


@router.get(
    "",
    response_model=list[ActivityLogResponse],
)
async def get_activity_logs(
    current_user: User = Depends(require_active_user),
    service: ActivityLogService = Depends(
        get_activity_log_service
    ),
) -> list[ActivityLogResponse]:
    """
    Get all activity logs.
    """

    return await service.get_all()


@router.get(
    "/latest",
    response_model=list[ActivityLogResponse],
)
async def get_latest_activity_logs(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(require_active_user),
    service: ActivityLogService = Depends(
        get_activity_log_service
    ),
) -> list[ActivityLogResponse]:
    """
    Get latest activity logs.
    """

    return await service.get_latest(limit)


@router.get(
    "/{log_id}",
    response_model=ActivityLogResponse,
)
async def get_activity_log(
    log_id: int,
    current_user: User = Depends(require_active_user),
    service: ActivityLogService = Depends(
        get_activity_log_service
    ),
) -> ActivityLogResponse:
    """
    Get activity log by ID.
    """

    log = await service.get_by_id(log_id)

    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity log not found",
        )

    return log


@router.post(
    "",
    response_model=ActivityLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_activity_log(
    data: ActivityLogCreate,
    current_user: User = Depends(require_active_user),
    service: ActivityLogService = Depends(
        get_activity_log_service
    ),
) -> ActivityLogResponse:
    """
    Create activity log.
    """

    return await service.create(data)


@router.delete(
    "/{log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_activity_log(
    log_id: int,
    current_user: User = Depends(require_active_user),
    service: ActivityLogService = Depends(
        get_activity_log_service
    ),
) -> None:
    """
    Delete activity log by ID.
    """

    deleted = await service.delete(log_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity log not found",
        )