from datetime import datetime

from pydantic import BaseModel, Field


class ActivityLogBase(BaseModel):
    """
    Base schema for activity logs.
    """

    action: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Performed action name",
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        description="Additional activity details",
    )

    user_id: int | None = Field(
        default=None,
        description="Related user ID",
    )


class ActivityLogCreate(ActivityLogBase):
    """
    Schema for creating activity logs.
    """

    pass


class ActivityLogResponse(ActivityLogBase):
    """
    Activity log response schema.
    """

    id: int = Field(
        ...,
        description="Activity log ID",
    )

    created_at: datetime = Field(
        ...,
        description="Activity timestamp",
    )

    model_config = {
        "from_attributes": True,
    }


class ActivityLogListResponse(BaseModel):
    """
    Activity log list response schema.
    """

    items: list[ActivityLogResponse] = Field(
        default_factory=list,
        description="Activity logs list",
    )

    total: int = Field(
        default=0,
        ge=0,
        description="Total activity logs count",
    )