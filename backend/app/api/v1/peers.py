"""
Peer API endpoints.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import FileResponse, Response

from backend.app.api.dependencies import (
    get_config_generator_service,
    get_peer_service,
)
from backend.app.core.dependencies import require_active_user, require_peer_access
from backend.app.models.user import User
from backend.app.models.peer import Peer
from backend.app.schemas.peer import (
    PeerCreate,
    PeerResponse,
    PeerUpdate,
)
from backend.app.services.config_generator import ConfigGeneratorService
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
    Get peers visible to the current user.

    Superusers can access all peers.
    Regular users can access only their own peers.
    """

    if current_user.is_superuser:
        return await service.get_all()

    return await service.get_by_user(current_user.id)


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
    Get peers belonging to a user.

    Superusers can access any user's peers.
    Regular users can access only their own peers.
    """

    if not current_user.is_superuser and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this user's peers",
        )

    return await service.get_by_user(user_id)


@router.get(
    "/{peer_id}",
    response_model=PeerResponse,
)
async def get_peer(
    peer: Peer = Depends(require_peer_access),
) -> PeerResponse:
    """
    Get peer by ID.

    Access is enforced by require_peer_access.
    """

    return peer


@router.get(
    "/{peer_id}/config",
)
async def download_peer_config(
    peer: Peer = Depends(require_peer_access),
    config_service: ConfigGeneratorService = Depends(
        get_config_generator_service,
    ),
) -> Response:
    """
    Download peer AmneziaWG configuration.

    Access is enforced by require_peer_access.
    """

    if not peer.private_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Peer private key is not available",
        )

    config = config_service.generate(peer)

    return Response(
        content=config,
        media_type="text/plain",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{peer.name}.conf"'
            ),
        },
    )


@router.get(
    "/{peer_id}/qr",
)
async def download_peer_qr(
    peer: Peer = Depends(require_peer_access),
    config_service: ConfigGeneratorService = Depends(
        get_config_generator_service,
    ),
) -> FileResponse:
    """
    Download peer QR code.

    Access is enforced by require_peer_access.
    """

    if not peer.private_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Peer private key is not available",
        )

    qr_path = config_service.generate_qr(peer)

    return FileResponse(
        path=qr_path,
        media_type="image/png",
        filename=f"{peer.name}.png",
    )


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

    Superusers can create peers for any user.
    Regular users can create peers only for themselves.
    """

    if not current_user.is_superuser and data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create peers for yourself",
        )

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
    peer: Peer = Depends(require_peer_access),
    service: PeerService = Depends(get_peer_service),
) -> PeerResponse:
    """
    Update an existing peer.

    Access is enforced by require_peer_access.
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
    peer: Peer = Depends(require_peer_access),
    service: PeerService = Depends(get_peer_service),
) -> None:
    """
    Delete peer by ID.

    Access is enforced by require_peer_access.
    """

    deleted = await service.delete(peer_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peer not found",
        )

