"""Pydantic schemas for MCP tool inputs and outputs."""

from .common import APIResponse, ErrorDetail
from .request.sql import ExecuteSqlRequest
from .response.health import HealthResponse
from .response.schema import ColumnSchema, SchemaCatalogResponse, TableSchema
from .response.sql import SqlQueryResponse

__all__ = [
    "APIResponse",
    "ErrorDetail",
    "ExecuteSqlRequest",
    "HealthResponse",
    "ColumnSchema",
    "TableSchema",
    "SchemaCatalogResponse",
    "SqlQueryResponse",
]
