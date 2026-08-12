"""SQL query response schemas."""

from typing import Any

from pydantic import BaseModel, Field


class SqlQueryResponse(BaseModel):
    """Result set from a read-only SQL query."""

    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    row_count: int = 0
    truncated: bool = False
    sql_executed: str = ""
