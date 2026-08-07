from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.app.db.base import Base


class Traffic(Base):

    __tablename__ = "traffic"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )


    peer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "peers.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    upload_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )


    download_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


    peer = relationship(
        "Peer",
        back_populates="traffic",
    )