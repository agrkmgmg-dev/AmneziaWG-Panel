"""Device binding endpoints for the dedicated mobile client."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.dependencies import require_active_user
from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.repositories.peer import PeerRepository
from backend.app.schemas.device import DeviceBindRequest, DeviceBindResponse
from backend.app.services.awg_manager import AWGManagerService


router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("/bind", response_model=DeviceBindResponse)
async def bind_device(
    data: DeviceBindRequest,
    user: User = Depends(require_active_user),
    session: AsyncSession = Depends(get_db),
) -> DeviceBindResponse:
    """Bind the first app-generated public key to the user's only peer."""
    peer = next(iter(await PeerRepository(session).get_by_user(user.id)), None)
    if peer is None:
        raise HTTPException(status_code=404, detail="No VPN peer exists for this user")

    if peer.device_public_key and peer.device_public_key != data.public_key:
        raise HTTPException(status_code=409, detail="A different device is already bound")

    now = datetime.now(timezone.utc)
    if not peer.device_public_key:
        old_key = peer.public_key
        peer.device_public_key = data.public_key
        peer.device_bound_at = now
        peer.public_key = data.public_key
        peer.private_key = None
        await session.commit()
        try:
            manager = AWGManagerService()
            manager.remove_peer(old_key)
            manager.add_peer(data.public_key, peer.address)
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"VPN peer provisioning failed: {exc}") from exc

    return DeviceBindResponse(
        peer_id=peer.id,
        address=peer.address,
        endpoint=settings.AWG_ENDPOINT,
        server_public_key=settings.AWG_SERVER_PUBLIC_KEY,
        awg_params={
            "Jc": settings.AWG_JC,
            "Jmin": settings.AWG_JMIN,
            "Jmax": settings.AWG_JMAX,
            "S1": settings.AWG_S1,
            "S2": settings.AWG_S2,
            "S3": settings.AWG_S3,
            "S4": settings.AWG_S4,
            "H1": settings.AWG_H1,
            "H2": settings.AWG_H2,
            "H3": settings.AWG_H3,
            "H4": settings.AWG_H4,
        },
        bound_at=peer.device_bound_at or now,
    )
