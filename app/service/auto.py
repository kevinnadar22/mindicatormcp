"""Auto rickshaw fare service."""

from loguru import logger

from app.core import exceptions
from app.domain import schemas
from app.repository import MindicatorRepository


class AutoService:
    """Auto rickshaw tariff lookups."""

    def __init__(self, repo: MindicatorRepository) -> None:
        """Bind the Mindicator repository."""
        self._repo = repo

    async def get_fare(
        self, request: schemas.AutoFareRequest
    ) -> schemas.APIResponse[schemas.AutoFareResponse]:
        """Return day/night auto fare for a distance in km."""
        try:
            row = await self._repo.get_auto_fare_for_km(request.km)
            if row is None:
                raise exceptions.NotFoundError(
                    f"no auto fare found for {request.km} km"
                )
            data = schemas.AutoFareResponse(
                km=float(row["km"]),
                fare=int(row["fare"]),
                night_fare=int(row["night_fare"]),
            )
            logger.bind(km=request.km, fare=data.fare).info("auto fare ok")
            return schemas.APIResponse(data=data)
        except exceptions.AppError as exc:
            logger.bind(code=exc.code, error=exc.message).warning("auto fare failed")
            return schemas.APIResponse(
                error=schemas.ErrorDetail(code=exc.code, message=exc.message)
            )
