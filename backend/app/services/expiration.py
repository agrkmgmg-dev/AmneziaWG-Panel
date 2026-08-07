"""
Peer expiration manager.
"""

from datetime import datetime, timedelta


class ExpirationService:
    """
    Manage peer expiration status.
    """

    WARNING_DAYS = 7

    @staticmethod
    def is_expired(expires_at) -> bool:
        """
        Check expiration date.
        """

        if not expires_at:
            return False

        return expires_at < datetime.utcnow()


    @staticmethod
    def is_expiring_soon(expires_at) -> bool:
        """
        Check if peer expires soon.
        """

        if not expires_at:
            return False

        now = datetime.utcnow()

        warning_date = now + timedelta(
            days=ExpirationService.WARNING_DAYS
        )

        return now < expires_at <= warning_date


    @staticmethod
    def get_status(peer) -> str:
        """
        Return peer status.
        """

        if not peer.is_active:
            return "🔴 غیرفعال"


        if ExpirationService.is_expired(
            peer.expires_at
        ):
            return "🔴 منقضی شده"


        if ExpirationService.is_expiring_soon(
            peer.expires_at
        ):
            return "🟡 نزدیک انقضا"


        if peer.expires_at:
            return "🟢 فعال"


        return "⚪ بدون تاریخ"