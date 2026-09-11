"""
Admin peer service.

Provides peer management operations used by the
server-side Admin Panel.
"""

from datetime import datetime, timedelta
import time
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.peer import Peer
from backend.app.repositories.peer import PeerRepository
from backend.app.repositories.traffic import TrafficRepository

from backend.app.services.expiration import ExpirationService
from backend.app.services.ip_manager import IPManagerService
from backend.app.services.key_generator import KeyGeneratorService
from backend.app.services.usage_limit import UsageLimitService
from backend.app.services.config_import import parse_config
from backend.app.core.security import hash_password
from backend.app.repositories.user import UserRepository
from backend.app.services.awg_manager import AWGManagerService
from backend.app.services.wg_manager import WGManagerService
from backend.app.core.config import settings


class AdminPeerService:
    """
    Service for admin peer management.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

        self.peer_repository = PeerRepository(
            session
        )

        self.usage_service = UsageLimitService(
            TrafficRepository(session)
        )
        self.user_repository = UserRepository(session)

    @staticmethod
    def _manager(protocol: str):
        return WGManagerService() if protocol == "wireguard" else AWGManagerService()

    async def import_config(
        self,
        username: str,
        name: str,
        config_text: str,
        expires_at=None,
    ) -> Peer:
        """Import an existing client config and preserve its key material."""
        parsed = parse_config(config_text)
        user = await self.user_repository.get_by_username(username)
        if user is None:
            user = UserRepository(self.session).model(
                username=username,
                hashed_password=hash_password(f"imported-{username}-disabled"),
                is_active=True,
            )
            user = await self.user_repository.create(user)
        if await self.peer_repository.get_by_user(user.id):
            raise ValueError("این کاربر قبلاً یک دستگاه دارد")
        public_key = KeyGeneratorService.generate_public_key(parsed.private_key)
        existing = await self.peer_repository.get_by_public_key(public_key)
        if existing:
            raise ValueError("این کانفیگ قبلاً وارد شده است")
        protocol = "amneziawg" if parsed.amnezia_i1 else "wireguard"
        peer = Peer(
            user_id=user.id,
            name=name,
            public_key=public_key,
            private_key=parsed.private_key,
            preshared_key=parsed.preshared_key,
            amnezia_i1=parsed.amnezia_i1,
            protocol=protocol,
            address=parsed.address,
            expires_at=expires_at,
            is_active=True,
        )
        await self.peer_repository.create(peer)
        await self.session.refresh(peer)
        try:
            self._manager(protocol).add_peer(peer.public_key, peer.address, peer.preshared_key)
        except Exception:
            # Keep the database record; reconciliation can retry when the
            # host helper is temporarily unavailable.
            pass
        return peer

    async def _attach_status(
        self,
        peer: Peer,
    ) -> Peer:
        """
        Attach calculated statuses.
        """

        peer.status = ExpirationService.get_status(
            peer
        )

        peer.usage_status = (
            await self.usage_service.get_status(peer)
        )

        peer.usage_display = (
            await self.usage_service.get_display(peer)
        )

        return peer

    async def get_peers(
        self,
    ) -> list[Peer]:
        """
        Return all peers with calculated status.
        """

        peers = await self.peer_repository.get_all_with_users()

        for peer in peers:
            await self._attach_status(peer)

        return peers

    async def get_peer(
        self,
        peer_id: int,
    ) -> Peer | None:
        """
        Return one peer with calculated status.
        """

        peer = await self.peer_repository.get_by_id(
            peer_id
        )

        if peer is not None:
            await self._attach_status(peer)

        return peer

    async def create_peer(
        self,
        user_id: int,
        name: str,
        expires_at=None,
        traffic_limit_bytes=None,
        rate_limit_mbps=None,
        protocol: str = "amneziawg",
    ) -> Peer:
        """
        Create a peer with automatic keys and IP.
        """

        if protocol not in {"amneziawg", "wireguard"}:
            raise ValueError("نوع کانفیگ نامعتبر است")

        existing = await self.peer_repository.get_by_user(user_id)
        if existing:
            raise ValueError(
                "Each user is limited to one VPN device"
            )

        key_service = KeyGeneratorService()

        ip_service = IPManagerService(
            self.peer_repository,
            protocol=protocol,
        )

        private_key, public_key = (
            key_service.generate_keypair()
        )
        preshared_key = key_service.generate_preshared_key()

        address = await ip_service.get_next_ip()

        peer = Peer(
            user_id=user_id,
            name=name,
            public_key=public_key,
            preshared_key=preshared_key,
            protocol=protocol,
            amnezia_i1=settings.AWG_I1 if protocol == "amneziawg" else None,
            private_key=private_key,
            address=address,
            expires_at=expires_at,
            traffic_limit_bytes=traffic_limit_bytes,
            rate_limit_mbps=(
                rate_limit_mbps
                if rate_limit_mbps is not None
                else settings.AWG_PEER_RATE_LIMIT_MBPS or 15
            ),
            is_active=True,
        )

        peer = await self.peer_repository.create(peer)

        # A database record alone is not a usable VPN account. Provision the
        # peer on the live AmneziaWG interface before reporting success.
        auto_sync = settings.WG_AUTO_SYNC if protocol == "wireguard" else settings.AWG_AUTO_SYNC
        if auto_sync:
            try:
                manager = self._manager(protocol)
                last_error = None
                for attempt in range(3):
                    try:
                        manager.add_peer(peer.public_key, peer.address, peer.preshared_key)
                        if peer.rate_limit_mbps:
                            manager.set_rate_limit(peer.address, peer.rate_limit_mbps)
                        last_error = None
                        break
                    except Exception as exc:
                        last_error = exc
                        if attempt < 2:
                            time.sleep(0.4)
                if last_error is not None:
                    raise last_error
            except Exception as exc:
                await self.peer_repository.delete(peer)
                raise RuntimeError(
                    "VPN peer provisioning failed; no configuration was created"
                ) from exc

        return peer

    async def delete_peer(
        self,
        peer_id: int,
    ) -> bool:
        """
        Delete peer by ID.
        """

        peer = await self.peer_repository.get_by_id(
            peer_id
        )

        if peer is None:
            return False

        auto_sync = settings.WG_AUTO_SYNC if peer.protocol == "wireguard" else settings.AWG_AUTO_SYNC
        if auto_sync:
            try:
                self._manager(peer.protocol).remove_peer(peer.public_key)
            except Exception:
                # Continue deletion when the peer was already absent from the
                # live interface; the database must not retain a dead account.
                pass

        try:
            # Delete through the ORM relationship so associated traffic rows
            # are removed as well, even when SQLite foreign-key cascades are
            # disabled on an existing database.
            await self.session.delete(peer)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        return True

    async def extend_peer(
        self,
        peer_id: int,
        days: int,
        traffic_limit_gb: float | None = None,
    ) -> Peer | None:
        if days not in {0, 7, 30, 90, 365}:
            raise ValueError("مدت تمدید نامعتبر است")
        if traffic_limit_gb is not None and traffic_limit_gb <= 0:
            raise ValueError("حجم تمدید باید بیشتر از صفر باشد")
        peer = await self.peer_repository.get_by_id(peer_id)
        if peer is None:
            return None
        now = datetime.utcnow()
        if days:
            base = peer.expires_at if peer.expires_at and peer.expires_at > now else now
            peer.expires_at = base + timedelta(days=days)
        if traffic_limit_gb is not None:
            added_bytes = int(traffic_limit_gb * 1024**3)
            peer.traffic_limit_bytes = (peer.traffic_limit_bytes or 0) + added_bytes
        peer.is_active = True
        await self.session.commit()
        await self.session.refresh(peer)
        auto_sync = settings.WG_AUTO_SYNC if peer.protocol == "wireguard" else settings.AWG_AUTO_SYNC
        if auto_sync:
            # A peer that expired/used its quota was removed from live AWG.
            # Re-adding it makes renewal immediately usable without a new config.
            manager = self._manager(peer.protocol)
            manager.add_peer(
                peer.public_key,
                peer.address,
                peer.preshared_key,
            )
            if peer.rate_limit_mbps:
                manager.set_rate_limit(
                    peer.address,
                    peer.rate_limit_mbps,
                )
        return peer
