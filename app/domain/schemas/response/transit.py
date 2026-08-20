"""Train / bus / auto response schemas."""

from pydantic import BaseModel, Field


class StationItem(BaseModel):
    """One station match."""

    name: str
    lat: float | None = None
    lon: float | None = None


class StationSearchResponse(BaseModel):
    """Station search results."""

    stations: list[StationItem] = Field(default_factory=list)
    count: int = 0


class TrainPathItem(BaseModel):
    """One transfer-path hint between stations."""

    from_station: str
    to_station: str
    path_desc: str


class TrainPathResponse(BaseModel):
    """Train path hints between two stations."""

    paths: list[TrainPathItem] = Field(default_factory=list)
    count: int = 0


class TicketFareItem(BaseModel):
    """One OD ticket fare row (fare_1 is typical single second-class)."""

    src_station: str
    dst_station: str
    route_code: str
    fare_1: int | None = None
    fare_6: int | None = None


class TicketFareResponse(BaseModel):
    """Ticket fare rows for an OD pair."""

    fares: list[TicketFareItem] = Field(default_factory=list)
    count: int = 0


class BusRouteItem(BaseModel):
    """One bus route summary."""

    agency: str
    code: str
    stop_count: int


class BusRouteSearchResponse(BaseModel):
    """Bus route search results."""

    routes: list[BusRouteItem] = Field(default_factory=list)
    count: int = 0


class BusStopItem(BaseModel):
    """One stop on a bus route."""

    seq: int
    stop_name: str
    stop_index: int


class BusRouteStopsResponse(BaseModel):
    """Ordered stops for a bus route."""

    agency: str
    route_code: str
    stops: list[BusStopItem] = Field(default_factory=list)
    count: int = 0


class AutoFareResponse(BaseModel):
    """Auto rickshaw day/night fare for a given km."""

    km: float
    fare: int
    night_fare: int
