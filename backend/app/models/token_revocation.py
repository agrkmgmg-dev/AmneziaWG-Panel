"""
Token revocation model.

Stores revoked JWT identifiers (JTI) so that
logged-out tokens cannot be reused.
"""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class TokenRevocation(Base):
    """
    Represents a revoked JWT token.
    """

    __tablename__ = "token_revocations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    jti: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        index=True,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )