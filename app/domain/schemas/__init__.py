"""Pydantic schemas for MCP tool inputs and outputs."""

from .common import APIResponse, ErrorDetail
from .request.live import LiveTrainStatusRequest
from .request.sql import ExecuteSqlRequest
from .request.transit import (
    AutoFareRequest,
    BusRouteSearchRequest,
    BusRouteStopsRequest,
    StationPairRequest,
    StationSearchRequest,
)
from .response.health import HealthResponse
from .response.live import LiveTrainStatusResponse
from .response.schema import ColumnSchema, SchemaCatalogResponse, TableSchema
from .response.sql import SqlQueryResponse
from .response.transit import (
    AutoFareResponse,
    BusRouteItem,
    BusRouteSearchResponse,
    BusRouteStopsResponse,
    BusStopItem,
    StationItem,
    StationSearchResponse,
    TicketFareItem,
    TicketFareResponse,
    TrainPathItem,
    TrainPathResponse,
)

__all__ = [
    "APIResponse",
    "ErrorDetail",
    "ExecuteSqlRequest",
    "LiveTrainStatusRequest",
    "StationSearchRequest",
    "StationPairRequest",
    "BusRouteSearchRequest",
    "BusRouteStopsRequest",
    "AutoFareRequest",
    "HealthResponse",
    "LiveTrainStatusResponse",
    "ColumnSchema",
    "TableSchema",
    "SchemaCatalogResponse",
    "SqlQueryResponse",
    "StationItem",
    "StationSearchResponse",
    "TrainPathItem",
    "TrainPathResponse",
    "TicketFareItem",
    "TicketFareResponse",
    "BusRouteItem",
    "BusRouteSearchResponse",
    "BusStopItem",
    "BusRouteStopsResponse",
    "AutoFareResponse",
]
