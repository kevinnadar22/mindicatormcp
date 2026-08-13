"""Live train status response schemas."""

from pydantic import BaseModel


class LiveTrainStatusResponse(BaseModel):
    """Live tracker status for one train number."""

    train_no: str
    found: bool
    status: str
    origin: str | None = None
    destination: str | None = None
    line_code: str | None = None
