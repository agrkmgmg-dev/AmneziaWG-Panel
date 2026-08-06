from datetime import datetime

from pydantic import BaseModel, Field


class TrafficBase(BaseModel):
    """
    Base traffic schema.
    """

    peer_id: int = Field(
        ...,
        description="Related peer ID",
    )

    upload_bytes: int = Field(
        default=0,
        ge=0,
        description="Uploaded traffic in bytes",
    )

    download_bytes: int = Field(
        default=0,
        ge=0,
        description="Downloaded traffic in bytes",
    )


class TrafficCreate(TrafficBase):
    """
    Schema for creating traffic records.
    """

    pass


class TrafficResponse(TrafficBase):
    """
    Traffic record response schema.
    """

    id: int = Field(
        ...,
        description="Traffic record ID",
    )

    created_at: datetime = Field(
        ...,
        description="Traffic record creation time",
    )

    model_config = {
        "from_attributes": True,
    }


class TrafficSummaryResponse(BaseModel):
    """
    Aggregated traffic summary.
    """

    peer_id: int = Field(
        ...,
        description="Peer ID",
    )

    total_upload_bytes: int = Field(
        default=0,
        ge=0,
        description="Total uploaded bytes",
    )

    total_download_bytes: int = Field(
        default=0,
        ge=0,
        description="Total downloaded bytes",
    )

    total_bytes: int = Field(
        default=0,
        ge=0,
        description="Total traffic usage",
    )


class TrafficListResponse(BaseModel):
    """
    Traffic list response.
    """

    items: list[TrafficResponse] = Field(
        default_factory=list,
        description="Traffic records list",
    )

    total: int = Field(
        default=0,
        ge=0,
        description="Total records count",
    )