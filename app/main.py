"""FastMCP entrypoint for the Mindicator SQLite server."""

from fastmcp import FastMCP
from loguru import logger

from app.core import config
from app.core import logging as app_logging
from app.domain import schemas
from app.repository import MindicatorRepository
from app.service import health as health_service
from app.service import schema as schema_service
from app.service import sql_query


def build_mcp() -> FastMCP:
    """Create FastMCP with startup schema cache and three tools."""
    app_logging.setup_logging()
    repo = MindicatorRepository(config.settings.db_path)
    schema_svc = schema_service.SchemaService(repo)
    catalog = schema_svc.load_and_cache()
    instructions = schema_svc.format_instructions(catalog)

    mcp = FastMCP(
        name=config.settings.service_name,
        instructions=instructions,
        version=config.settings.service_version,
    )
    health_svc = health_service.HealthService(repo)
    sql_svc = sql_query.SqlQueryService(repo)

    @mcp.tool
    async def health_check() -> schemas.APIResponse[schemas.HealthResponse]:
        """Health check: service status and Mindicator DB meta."""
        return health_svc.check()

    @mcp.tool
    async def get_schema() -> schemas.APIResponse[schemas.SchemaCatalogResponse]:
        """Return the full cached DB catalog (tables, columns, descriptions)."""
        return schema_svc.get_catalog()

    @mcp.tool
    async def execute_sql(sql: str) -> schemas.APIResponse[schemas.SqlQueryResponse]:
        """Run a read-only SELECT/WITH query. LIMIT is enforced by the server."""
        return sql_svc.execute(schemas.ExecuteSqlRequest(sql=sql))

    logger.bind(tools=["health_check", "get_schema", "execute_sql"]).info(
        "fastmcp ready"
    )
    return mcp


def main() -> None:
    """Run the Mindicator MCP server over HTTP (streamable)."""
    settings = config.settings
    logger.bind(host=settings.host, port=settings.port).info("starting http transport")
    build_mcp().run(transport="http", host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
