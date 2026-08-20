"""Train / bus / auto request schemas."""

from pydantic import BaseModel, Field


class StationSearchRequest(BaseModel):
    """Search stations by name fragment."""

    query: str = Field(..., min_length=1, description="Station name fragment, e.g. BANDRA")


class StationPairRequest(BaseModel):
    """Origin and destination station names."""

    from_station: str = Field(..., min_length=1, description="Origin station name")
    to_station: str = Field(..., min_length=1, description="Destination station name")


class BusRouteSearchRequest(BaseModel):
    """Search bus routes by code or agency."""

    query: str = Field(..., min_length=1, description="Route code fragment, e.g. 1(Up)")
    agency: str | None = Field(None, description="Optional agency filter, e.g. BEST")


class BusRouteStopsRequest(BaseModel):
    """List stops on one bus route."""

    agency: str = Field(..., min_length=1, description="Agency code, e.g. BEST")
    route_code: str = Field(..., min_length=1, description="Route code, e.g. 1(Up)")


class AutoFareRequest(BaseModel):
    """Auto rickshaw fare for a distance in km."""

    km: float = Field(..., gt=0, description="Trip distance in kilometres")
