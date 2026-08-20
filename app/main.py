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
from app.service import auto as auto_service
from app.service import bus as bus_service
from app.service import health as health_service
from app.service import live_train as live_train_service
from app.service import schema as schema_service
from app.service import sql_query
from app.service import train as train_service


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
    train_svc = train_service.TrainService(repo)
    bus_svc = bus_service.BusService(repo)
    auto_svc = auto_service.AutoService(repo)

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

    # --- existing tools (kept) ---

    @mcp.tool(title="Check Health", tags={"meta"})
    async def health_check() -> schemas.APIResponse[schemas.HealthResponse]:
        """Health check: service status and Mindicator DB meta."""
        return await health_svc.check()

    @mcp.tool(title="List Database Tables", tags={"meta"})
    async def get_schema() -> schemas.APIResponse[schemas.SchemaCatalogResponse]:
        """Return the full cached DB catalog (tables, columns, descriptions)."""
        return await schema_svc.get_catalog()

    @mcp.tool(title="Run SQL Query", tags={"sql"})
    async def execute_sql(sql: str) -> schemas.APIResponse[schemas.SqlQueryResponse]:
        """Run a read-only SELECT/WITH query. LIMIT is enforced by the server."""
        return await sql_svc.execute(schemas.ExecuteSqlRequest(sql=sql))

    @mcp.tool(title="Live Train Status", tags={"train"})
    async def get_live_status(
        train_no: str,
    ) -> schemas.APIResponse[schemas.LiveTrainStatusResponse]:
        """Live running status for a suburban train number (e.g. 95338)."""
        return await live_svc.get_status(schemas.LiveTrainStatusRequest(train_no=train_no))

    # --- train ---

    @mcp.tool(title="Search Train Stations", tags={"train"})
    async def search_stations(
        query: str,
    ) -> schemas.APIResponse[schemas.StationSearchResponse]:
        """Search suburban train stations by name fragment (e.g. BANDRA)."""
        return await train_svc.search_stations(schemas.StationSearchRequest(query=query))

    @mcp.tool(title="Find Train Path", tags={"train"})
    async def find_train_path(
        from_station: str,
        to_station: str,
    ) -> schemas.APIResponse[schemas.TrainPathResponse]:
        """Find path hints between two stations (e.g. CHURCHGATE to THANE)."""
        return await train_svc.find_path(
            schemas.StationPairRequest(from_station=from_station, to_station=to_station)
        )

    @mcp.tool(title="Get Ticket Fare", tags={"train"})
    async def get_ticket_fare(
        from_station: str,
        to_station: str,
    ) -> schemas.APIResponse[schemas.TicketFareResponse]:
        """Get suburban ticket fares between two stations."""
        return await train_svc.get_ticket_fare(
            schemas.StationPairRequest(from_station=from_station, to_station=to_station)
        )

    # --- bus ---

    @mcp.tool(title="Search Bus Routes", tags={"bus"})
    async def search_bus_routes(
        query: str,
        agency: str | None = None,
    ) -> schemas.APIResponse[schemas.BusRouteSearchResponse]:
        """Search bus routes by code (e.g. 1(Up)); optional agency like BEST."""
        return await bus_svc.search_routes(
            schemas.BusRouteSearchRequest(query=query, agency=agency)
        )

    @mcp.tool(title="Get Bus Route Stops", tags={"bus"})
    async def get_bus_route_stops(
        agency: str,
        route_code: str,
    ) -> schemas.APIResponse[schemas.BusRouteStopsResponse]:
        """List ordered stops on a bus route (e.g. BEST, 1(Up))."""
        return await bus_svc.get_route_stops(
            schemas.BusRouteStopsRequest(agency=agency, route_code=route_code)
        )

    # --- auto ---

    @mcp.tool(title="Get Auto Fare", tags={"auto"})
    async def get_auto_fare(km: float) -> schemas.APIResponse[schemas.AutoFareResponse]:
        """Get auto rickshaw day/night fare for a distance in km."""
        return await auto_svc.get_fare(schemas.AutoFareRequest(km=km))

    logger.bind(
        tools=[
            "health_check",
            "get_schema",
            "execute_sql",
            "get_live_status",
            "search_stations",
            "find_train_path",
            "get_ticket_fare",
            "search_bus_routes",
            "get_bus_route_stops",
            "get_auto_fare",
        ]
    ).info("fastmcp ready")
    return mcp


def main() -> None:
    """Run the Mindicator MCP server over HTTP (streamable)."""
    settings = config.settings
    logger.bind(host=settings.host, port=settings.port).info("starting http transport")
    build_mcp().run(transport="http", host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
