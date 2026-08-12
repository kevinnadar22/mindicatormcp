"""SQL-related request schemas."""

from pydantic import BaseModel, Field


class ExecuteSqlRequest(BaseModel):
    """Request body for a read-only SQL query."""

    sql: str = Field(..., min_length=1, description="SELECT or WITH statement")
