"""Pydantic schemas for MCP tool inputs and outputs."""

from .common import APIResponse, ErrorDetail
from .request.live import LiveTrainStatusRequest
from .request.sql import ExecuteSqlRequest
from .response.health import HealthResponse
from .response.live import LiveTrainStatusResponse
from .response.schema import ColumnSchema, SchemaCatalogResponse, TableSchema
from .response.sql import SqlQueryResponse

__all__ = [
    "APIResponse",
    "ErrorDetail",
    "ExecuteSqlRequest",
    "LiveTrainStatusRequest",
    "HealthResponse",
    "LiveTrainStatusResponse",
    "ColumnSchema",
    "TableSchema",
    "SchemaCatalogResponse",
    "SqlQueryResponse",
]
