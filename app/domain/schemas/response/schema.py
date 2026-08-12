"""Schema catalog response models."""

from pydantic import BaseModel, Field


class ColumnSchema(BaseModel):
    """One column from PRAGMA table_info."""

    name: str
    type: str
    notnull: bool = False
    pk: bool = False


class TableSchema(BaseModel):
    """One user table with columns and description."""

    name: str
    category: str
    description: str
    row_count: int = 0
    columns: list[ColumnSchema] = Field(default_factory=list)


class SchemaCatalogResponse(BaseModel):
    """Full database catalog returned by get_schema."""

    city: str | None = None
    db_version: str | None = None
    table_count: int = 0
    tables: list[TableSchema] = Field(default_factory=list)
