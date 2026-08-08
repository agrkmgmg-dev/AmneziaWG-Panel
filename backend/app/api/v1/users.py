"""
User API endpoints.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from backend.app.api.dependencies import get_user_service
from backend.app.core.dependencies import require_active_user
from backend.app.models.user import User
from backend.app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
)
from backend.app.services.user import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=list[UserResponse],
)
async def get_users(
    current_user: User = Depends(require_active_user),
    service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    """
    Get all users.
    """

    return await service.get_all()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_active_user),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Get user by ID.
    """

    user = await service.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data: UserCreate,
    current_user: User = Depends(require_active_user),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Create new user.
    """

    try:
        return await service.create(data)

    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists",
            ) from exc

        raise


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: User = Depends(require_active_user),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Update an existing user.
    """

    try:
        user = await service.update(
            user_id,
            data,
        )

    except ValueError as exc:
        if str(exc) == "Username already exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists",
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_active_user),
    service: UserService = Depends(get_user_service),
) -> None:
    """
    Delete user by ID.
    """

    deleted = await service.delete(user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )