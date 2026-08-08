"""
Peer API endpoints.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from backend.app.api.dependencies import get_peer_service
from backend.app.core.dependencies import require_active_user
from backend.app.models.user import User
from backend.app.schemas.peer import (
    PeerCreate,
    PeerResponse,
    PeerUpdate,
)
from backend.app.services.peer import PeerService


router = APIRouter(
    prefix="/peers",
    tags=["Peers"],
)


@router.get(
    "",
    response_model=list[PeerResponse],
)
async def get_peers(
    current_user: User = Depends(require_active_user),
    service: PeerService = Depends(get_peer_service),
) -> list[PeerResponse]:
    """
    Get all peers.
    """

    return await service.get_all()


@router.get(
    "/user/{user_id}",
    response_model=list[PeerResponse],
)
async def get_user_peers(
    user_id: int,
    current_user: User = Depends(require_active_user),
    service: PeerService = Depends(get_peer_service),
) -> list[PeerResponse]:
    """
    Get all peers belonging to a user.
    """

    return await service.get_by_user(user_id)


@router.get(
    "/{peer_id}",
    response_model=PeerResponse,
)
async def get_peer(
    peer_id: int,
    current_user: User = Depends(require_active_user),
    service: PeerService = Depends(get_peer_service),
) -> PeerResponse:
    """
    Get peer by ID.
    """

    peer = await service.get_by_id(peer_id)

    if peer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peer not found",
        )

    return peer


@router.post(
    "",
    response_model=PeerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_peer(
    data: PeerCreate,
    current_user: User = Depends(require_active_user),
    service: PeerService = Depends(get_peer_service),
) -> PeerResponse:
    """
    Create a new peer.
    """

    try:
        return await service.create(data)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.put(
    "/{peer_id}",
    response_model=PeerResponse,
)
async def update_peer(
    peer_id: int,
    data: PeerUpdate,
    current_user: User = Depends(require_active_user),
    service: PeerService = Depends(get_peer_service),
) -> PeerResponse:
    """
    Update an existing peer.
    """

    try:
        peer = await service.update(
            peer_id,
            data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if peer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peer not found",
        )

    return peer


@router.delete(
    "/{peer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_peer(
    peer_id: int,
    current_user: User = Depends(require_active_user),
    service: PeerService = Depends(get_peer_service),
) -> None:
    """
    Delete peer by ID.
    """

    deleted = await service.delete(peer_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peer not found",
        )