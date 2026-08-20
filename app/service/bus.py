"""Bus route query service."""

from loguru import logger

from app.core import config, exceptions
from app.domain import schemas
from app.repository import MindicatorRepository


class BusService:
    """Bus route search and stop lists."""

    def __init__(self, repo: MindicatorRepository) -> None:
        """Bind the Mindicator repository."""
        self._repo = repo

    async def search_routes(
        self, request: schemas.BusRouteSearchRequest
    ) -> schemas.APIResponse[schemas.BusRouteSearchResponse]:
        """Search bus routes by code fragment."""
        try:
            agency = request.agency.strip() if request.agency else None
            rows = await self._repo.search_bus_routes(
                request.query.strip(), agency, config.settings.sql_row_limit
            )
            routes = [
                schemas.BusRouteItem(
                    agency=str(r["agency"]),
                    code=str(r["code"]),
                    stop_count=int(r["stop_count"]),
                )
                for r in rows
            ]
            data = schemas.BusRouteSearchResponse(routes=routes, count=len(routes))
            logger.bind(query=request.query, count=data.count).info("bus route search ok")
            return schemas.APIResponse(data=data)
        except exceptions.AppError as exc:
            logger.bind(code=exc.code, error=exc.message).warning("bus route search failed")
            return schemas.APIResponse(
                error=schemas.ErrorDetail(code=exc.code, message=exc.message)
            )

    async def get_route_stops(
        self, request: schemas.BusRouteStopsRequest
    ) -> schemas.APIResponse[schemas.BusRouteStopsResponse]:
        """List ordered stops on a bus route."""
        try:
            rows = await self._repo.get_bus_route_stops(
                request.agency.strip(),
                request.route_code.strip(),
                config.settings.sql_row_limit,
            )
            stops = [
                schemas.BusStopItem(
                    seq=int(r["seq"]),
                    stop_name=str(r["stop_name"]),
                    stop_index=int(r["stop_index"]),
                )
                for r in rows
            ]
            data = schemas.BusRouteStopsResponse(
                agency=request.agency.strip(),
                route_code=request.route_code.strip(),
                stops=stops,
                count=len(stops),
            )
            logger.bind(
                agency=data.agency, route_code=data.route_code, count=data.count
            ).info("bus route stops ok")
            return schemas.APIResponse(data=data)
        except exceptions.AppError as exc:
            logger.bind(code=exc.code, error=exc.message).warning("bus route stops failed")
            return schemas.APIResponse(
                error=schemas.ErrorDetail(code=exc.code, message=exc.message)
            )
