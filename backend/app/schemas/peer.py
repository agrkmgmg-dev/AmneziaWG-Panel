from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PeerBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Peer display name",
    )

    address: str | None = Field(
        default=None,
        description=(
            "WireGuard client address. "
            "Automatically assigned if omitted."
        ),
    )

    expires_at: datetime | None = Field(
        default=None,
        description="Peer expiration date",
    )


class PeerCreate(PeerBase):
    user_id: int = Field(
        ...,
        description="Owner user id",
    )


class PeerUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    is_active: bool | None = None

    expires_at: datetime | None = None


class PeerResponse(PeerBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int
    public_key: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PeerDetailResponse(PeerResponse):
    total_bytes: int = 0


class PeerListResponse(BaseModel):
    items: list[PeerResponse]
    total: int