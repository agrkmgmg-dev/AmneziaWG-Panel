from datetime import datetime

from pydantic import BaseModel, Field


class DeviceBindRequest(BaseModel):
    public_key: str = Field(..., min_length=44, max_length=44)


class DeviceBindResponse(BaseModel):
    peer_id: int
    address: str
    endpoint: str
    server_public_key: str
    awg_params: dict[str, int | str]
    bound_at: datetime
