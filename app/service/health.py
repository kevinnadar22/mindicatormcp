"""Health check service."""

from loguru import logger

from app.core import config, exceptions
from app.domain import schemas
from app.repository import MindicatorRepository


class HealthService:
    """Reports service and database health."""

    def __init__(self, repo: MindicatorRepository) -> None:
        """Bind the repository used for meta checks."""
        self._repo = repo

    async def check(self) -> schemas.APIResponse[schemas.HealthResponse]:
        """Return health status including city and DB version from meta."""
        try:
            meta = await self._repo.get_meta()
            data = schemas.HealthResponse(
                status="healthy",
                service=config.settings.service_name,
                version=config.settings.service_version,
                city=meta.get("city"),
                db_version=meta.get("version"),
                db_ok=True,
            )
            logger.bind(city=data.city, db_version=data.db_version).info("health ok")
            return schemas.APIResponse(data=data)
        except exceptions.AppError as exc:
            logger.bind(code=exc.code, error=exc.message).error("health failed")
            return schemas.APIResponse(
                data=schemas.HealthResponse(
                    status="unhealthy",
                    service=config.settings.service_name,
                    version=config.settings.service_version,
                    db_ok=False,
                ),
                error=schemas.ErrorDetail(code=exc.code, message=exc.message),
            )
