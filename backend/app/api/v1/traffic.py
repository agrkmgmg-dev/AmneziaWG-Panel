from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.dependencies import get_traffic_service
from backend.app.schemas.traffic import TrafficCreate, TrafficResponse
from backend.app.services.traffic import TrafficService


"""
Traffic API router.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from backend.app.api.dependencies import (
    get_traffic_service,
)

from backend.app.schemas.traffic import (
    TrafficCreate,
    TrafficResponse,
)

from backend.app.services.traffic import (
    TrafficService,
)


router = APIRouter(
    prefix="/traffic",
    tags=["Traffic"],
)


@router.get(
    "",
    response_model=list[TrafficResponse],
)
async def get_traffic_records(
    service: TrafficService = Depends(
        get_traffic_service
    ),
) -> list[TrafficResponse]:
    """
    Get all traffic records.
    """

    return await service.get_all()



@router.get(
    "/{traffic_id}",
    response_model=TrafficResponse,
)
async def get_traffic(
    traffic_id: int,
    service: TrafficService = Depends(
        get_traffic_service
    ),
) -> TrafficResponse:
    """
    Get traffic record by ID.
    """

    traffic = await service.get_by_id(
        traffic_id
    )

    if traffic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Traffic record not found",
        )

    return traffic



@router.post(
    "",
    response_model=TrafficResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_traffic(
    data: TrafficCreate,
    service: TrafficService = Depends(
        get_traffic_service
    ),
) -> TrafficResponse:
    """
    Create traffic record.
    """

    return await service.create(
        data
    )



@router.delete(
    "/{traffic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_traffic(
    traffic_id: int,
    service: TrafficService = Depends(
        get_traffic_service
    ),
) -> None:
    """
    Delete traffic record by ID.
    """

    deleted = await service.delete(
        traffic_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Traffic record not found",
        )



@router.get(
    "/peer/{peer_id}/usage",
)
async def get_peer_usage(
    peer_id: int,
    service: TrafficService = Depends(
        get_traffic_service
    ),
) -> dict:
    """
    Get traffic usage of a peer.
    """

    return await service.get_usage(
        peer_id
    )



@router.get(
    "/peer/{peer_id}/limit/{limit_bytes}",
)
async def check_peer_limit(
    peer_id: int,
    limit_bytes: int,
    service: TrafficService = Depends(
        get_traffic_service
    ),
) -> dict:
    """
    Check peer traffic limit.
    """

    return await service.check_limit(
        peer_id,
        limit_bytes,
    )