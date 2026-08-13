"""Schema catalog service with startup cache."""

from __future__ import annotations

from loguru import logger

from app.core import exceptions
from app.domain import schemas
from app.repository import MindicatorRepository
from app.service import table_catalog


class SchemaService:
    """Builds and caches the full DB schema catalog."""

    def __init__(self, repo: MindicatorRepository) -> None:
        """Bind repository and empty cache."""
        self._repo = repo
        self._cache: schemas.SchemaCatalogResponse | None = None

    async def load_and_cache(self) -> schemas.SchemaCatalogResponse:
        """Load catalog from SQLite once and keep it in memory."""
        catalog = await self._build_catalog()
        self._cache = catalog
        logger.bind(table_count=catalog.table_count).info("schema catalog cached")
        return catalog

    async def get_catalog(self) -> schemas.APIResponse[schemas.SchemaCatalogResponse]:
        """Return the cached catalog wrapped in APIResponse."""
        try:
            if self._cache is None:
                await self.load_and_cache()
            assert self._cache is not None
            return schemas.APIResponse(data=self._cache)
        except exceptions.AppError as exc:
            logger.bind(code=exc.code, error=exc.message).error("get_schema failed")
            return schemas.APIResponse(
                error=schemas.ErrorDetail(code=exc.code, message=exc.message)
            )

    def format_instructions(self, catalog: schemas.SchemaCatalogResponse) -> str:
        """Format catalog text for FastMCP server instructions."""
        lines = [
            "You are connected to the Mumbai Mindicator read-only SQLite database.",
            "Use execute_sql for timetable/fare/route questions.",
            "Use get_live_status(train_no) for live running status of a suburban train.",
            "Prefer get_schema only if you need structured JSON.",
            f"City: {catalog.city or 'unknown'} | DB version: {catalog.db_version or 'unknown'}",
            f"Tables ({catalog.table_count}):",
        ]
        for table in catalog.tables:
            cols = ", ".join(f"{c.name}:{c.type}" for c in table.columns)
            lines.append(
                f"- {table.name} [{table.category}] ({table.row_count} rows): "
                f"{table.description} | columns: {cols}"
            )
        return "\n".join(lines)

    async def _build_catalog(self) -> schemas.SchemaCatalogResponse:
        """Introspect all user tables and merge static descriptions."""
        meta = await self._repo.get_meta()
        tables: list[schemas.TableSchema] = []
        for name in await self._repo.list_user_tables():
            category, description = table_catalog.get_entry(name)
            columns = [
                schemas.ColumnSchema(
                    name=col["name"],
                    type=col["type"],
                    notnull=col["notnull"],
                    pk=col["pk"],
                )
                for col in await self._repo.get_columns(name)
            ]
            tables.append(
                schemas.TableSchema(
                    name=name,
                    category=category,
                    description=description,
                    row_count=await self._repo.count_rows(name),
                    columns=columns,
                )
            )
        return schemas.SchemaCatalogResponse(
            city=meta.get("city"),
            db_version=meta.get("version"),
            table_count=len(tables),
            tables=tables,
        )
