"""Health response schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health status returned by health_check."""

    status: str
    service: str
    version: str
    city: str | None = None
    db_version: str | None = None
    db_ok: bool = False
