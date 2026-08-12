"""
Traffic API router.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from backend.app.api.dependencies import get_traffic_service
from backend.app.core.dependencies import (
    require_active_user,
    require_peer_access,
)
from backend.app.models.user import User
from backend.app.models.peer import Peer
from backend.app.schemas.traffic import (
    TrafficCreate,
    TrafficResponse,
    TrafficSummaryResponse,
)
from backend.app.services.traffic import TrafficService


router = APIRouter(
    prefix="/traffic",
    tags=["Traffic"],
)


@router.get(
    "",
    response_model=list[TrafficResponse],
)
async def get_traffic_records(
    current_user: User = Depends(require_active_user),
    service: TrafficService = Depends(get_traffic_service),
) -> list[TrafficResponse]:
    """
    Get traffic records visible to the current user.

    Superusers can see all traffic records.
    Regular users can see only traffic belonging
    to their own peers.
    """

    if current_user.is_superuser:
        return await service.get_all()

    return await service.get_by_user(
        current_user.id
    )


@router.get(
    "/peer/{peer_id}/usage",
)
async def get_peer_usage(
    peer: Peer = Depends(require_peer_access),
    service: TrafficService = Depends(get_traffic_service),
) -> TrafficSummaryResponse:
    """
    Get traffic usage of a peer.
    """

    return await service.get_summary(peer.id)


@router.get(
    "/peer/{peer_id}/limit/{limit_bytes}",
)
async def check_peer_limit(
    peer: Peer = Depends(require_peer_access),
    limit_bytes: int = 0,
    service: TrafficService = Depends(get_traffic_service),
) -> TrafficSummaryResponse:
    """
    Check peer traffic limit.
    """

    if limit_bytes < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Traffic limit cannot be negative",
        )

    return await service.check_limit(
        peer.id,
        limit_bytes,
    )


@router.get(
    "/{traffic_id}",
    response_model=TrafficResponse,
)
async def get_traffic(
    traffic_id: int,
    current_user: User = Depends(require_active_user),
    service: TrafficService = Depends(get_traffic_service),
) -> TrafficResponse:
    """
    Get traffic record by ID.

    Ownership is enforced through the traffic record's peer.
    """

    traffic = await service.get_by_id(traffic_id)

    if traffic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Traffic record not found",
        )

    if not current_user.is_superuser:
        peer = await service.repository.get_peer_by_traffic_id(
            traffic_id
        )

        if peer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Peer not found",
            )

        if peer.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this traffic record",
            )

    return traffic


@router.post(
    "",
    response_model=TrafficResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_traffic(
    data: TrafficCreate,
    current_user: User = Depends(require_active_user),
    service: TrafficService = Depends(get_traffic_service),
) -> TrafficResponse:
    """
    Create traffic record.

    Users can create traffic only for their own peers.
    Superusers can create traffic for any peer.
    """

    peer = await service.repository.session.get(
        Peer,
        data.peer_id,
    )

    if peer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peer not found",
        )

    if not current_user.is_superuser and peer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this peer",
        )

    return await service.create(data)


@router.delete(
    "/{traffic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_traffic(
    traffic_id: int,
    current_user: User = Depends(require_active_user),
    service: TrafficService = Depends(get_traffic_service),
) -> None:
    """
    Delete traffic record.

    Users can delete only traffic belonging to their own peers.
    Superusers can delete any traffic record.
    """

    traffic = await service.get_by_id(traffic_id)

    if traffic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Traffic record not found",
        )

    if not current_user.is_superuser:
        peer = await service.repository.get_peer_by_traffic_id(
            traffic_id
        )

        if peer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Peer not found",
            )

        if peer.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this traffic record",
            )

    deleted = await service.delete(traffic_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Traffic record not found",
        )

