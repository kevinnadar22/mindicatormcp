"""FastMCP entrypoint for the Mindicator SQLite server."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from loguru import logger

from app.core import config
from app.core import logging as app_logging
from app.domain import schemas
from app.repository import MindicatorRepository
from app.service import health as health_service
from app.service import live_train as live_train_service
from app.service import schema as schema_service
from app.service import sql_query


def build_mcp() -> FastMCP:
    """Create FastMCP with startup schema cache and tools."""
    app_logging.setup_logging()
    repo = MindicatorRepository(config.settings.db_path)
    schema_svc = schema_service.SchemaService(repo)
    catalog = asyncio.run(schema_svc.load_and_cache())
    instructions = schema_svc.format_instructions(catalog)
    health_svc = health_service.HealthService(repo)
    sql_svc = sql_query.SqlQueryService(repo)
    live_svc = live_train_service.LiveTrainService(repo)

    @asynccontextmanager
    async def lifespan(_server: FastMCP) -> AsyncIterator[None]:
        """Close the live HTTP client when the server shuts down."""
        yield
        await live_svc.aclose()

    mcp = FastMCP(
        name=config.settings.service_name,
        instructions=instructions,
        version=config.settings.service_version,
        lifespan=lifespan,
    )

    @mcp.tool
    async def health_check() -> schemas.APIResponse[schemas.HealthResponse]:
        """Health check: service status and Mindicator DB meta."""
        return await health_svc.check()

    @mcp.tool
    async def get_schema() -> schemas.APIResponse[schemas.SchemaCatalogResponse]:
        """Return the full cached DB catalog (tables, columns, descriptions)."""
        return await schema_svc.get_catalog()

    @mcp.tool
    async def execute_sql(sql: str) -> schemas.APIResponse[schemas.SqlQueryResponse]:
        """Run a read-only SELECT/WITH query. LIMIT is enforced by the server."""
        return await sql_svc.execute(schemas.ExecuteSqlRequest(sql=sql))

    @mcp.tool
    async def get_live_status(
        train_no: str,
    ) -> schemas.APIResponse[schemas.LiveTrainStatusResponse]:
        """Live running status for a suburban train number (e.g. 95338)."""
        return await live_svc.get_status(schemas.LiveTrainStatusRequest(train_no=train_no))

    logger.bind(
        tools=["health_check", "get_schema", "execute_sql", "get_live_status"]
    ).info("fastmcp ready")
    return mcp


def main() -> None:
    """Run the Mindicator MCP server over HTTP (streamable)."""
    settings = config.settings
    logger.bind(host=settings.host, port=settings.port).info("starting http transport")
    build_mcp().run(transport="http", host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
