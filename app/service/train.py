"""Suburban train query service."""

from loguru import logger

from app.core import config, exceptions
from app.domain import schemas
from app.repository import MindicatorRepository


class TrainService:
    """Station search, path hints, and ticket fares."""

    def __init__(self, repo: MindicatorRepository) -> None:
        """Bind the Mindicator repository."""
        self._repo = repo

    async def search_stations(
        self, request: schemas.StationSearchRequest
    ) -> schemas.APIResponse[schemas.StationSearchResponse]:
        """Search stations by name fragment."""
        try:
            rows = await self._repo.search_stations(
                request.query.strip(), config.settings.sql_row_limit
            )
            stations = [
                schemas.StationItem(
                    name=str(r["name"]),
                    lat=r.get("lat"),
                    lon=r.get("lon"),
                )
                for r in rows
            ]
            data = schemas.StationSearchResponse(stations=stations, count=len(stations))
            logger.bind(query=request.query, count=data.count).info("station search ok")
            return schemas.APIResponse(data=data)
        except exceptions.AppError as exc:
            logger.bind(code=exc.code, error=exc.message).warning("station search failed")
            return schemas.APIResponse(
                error=schemas.ErrorDetail(code=exc.code, message=exc.message)
            )

    async def find_path(
        self, request: schemas.StationPairRequest
    ) -> schemas.APIResponse[schemas.TrainPathResponse]:
        """Find transfer-path hints between two stations."""
        try:
            rows = await self._repo.find_transfer_paths(
                request.from_station.strip(),
                request.to_station.strip(),
                config.settings.sql_row_limit,
            )
            paths = [
                schemas.TrainPathItem(
                    from_station=str(r["from_station"]),
                    to_station=str(r["to_station"]),
                    path_desc=str(r["path_desc"]),
                )
                for r in rows
            ]
            data = schemas.TrainPathResponse(paths=paths, count=len(paths))
            logger.bind(
                from_station=request.from_station,
                to_station=request.to_station,
                count=data.count,
            ).info("train path ok")
            return schemas.APIResponse(data=data)
        except exceptions.AppError as exc:
            logger.bind(code=exc.code, error=exc.message).warning("train path failed")
            return schemas.APIResponse(
                error=schemas.ErrorDetail(code=exc.code, message=exc.message)
            )

    async def get_ticket_fare(
        self, request: schemas.StationPairRequest
    ) -> schemas.APIResponse[schemas.TicketFareResponse]:
        """Look up ticket fares between two stations."""
        try:
            rows = await self._repo.find_ticket_fares(
                request.from_station.strip(),
                request.to_station.strip(),
                config.settings.sql_row_limit,
            )
            fares = [
                schemas.TicketFareItem(
                    src_station=str(r["src_station"]),
                    dst_station=str(r["dst_station"]),
                    route_code=str(r["route_code"]),
                    fare_1=r.get("fare_1"),
                    fare_6=r.get("fare_6"),
                )
                for r in rows
            ]
            data = schemas.TicketFareResponse(fares=fares, count=len(fares))
            logger.bind(count=data.count).info("ticket fare ok")
            return schemas.APIResponse(data=data)
        except exceptions.AppError as exc:
            logger.bind(code=exc.code, error=exc.message).warning("ticket fare failed")
            return schemas.APIResponse(
                error=schemas.ErrorDetail(code=exc.code, message=exc.message)
            )
