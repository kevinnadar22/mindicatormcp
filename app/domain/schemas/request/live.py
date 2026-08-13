"""Live train status request schemas."""

from pydantic import BaseModel, Field


class LiveTrainStatusRequest(BaseModel):
    """Request body for a live train lookup."""

    train_no: str = Field(..., min_length=1, description="Suburban train number")
