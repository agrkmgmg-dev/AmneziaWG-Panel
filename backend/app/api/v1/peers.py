from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.dependencies import get_peer_service
from backend.app.schemas.peer import PeerResponse
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
    service: PeerService = Depends(get_peer_service),
) -> list[PeerResponse]:
    """
    Get all peers.
    """

    return await service.get_all()


@router.get(
    "/{peer_id}",
    response_model=PeerResponse,
)
async def get_peer(
    peer_id: int,
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


@router.delete(
    "/{peer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_peer(
    peer_id: int,
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