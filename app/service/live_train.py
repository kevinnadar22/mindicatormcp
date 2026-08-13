"""Live train status service."""

from loguru import logger

from app.core import exceptions
from app.domain import schemas
from app.integrations import live_trains
from app.repository import MindicatorRepository


class LiveTrainService:
    """Looks up one train in the live tracker, then enriches from SQLite."""

    def __init__(
        self,
        repo: MindicatorRepository,
        client: live_trains.LiveTrainsClient | None = None,
    ) -> None:
        """Bind repository and live-trains HTTP client."""
        self._repo = repo
        self._client = client or live_trains.LiveTrainsClient()

    async def get_status(
        self, request: schemas.LiveTrainStatusRequest
    ) -> schemas.APIResponse[schemas.LiveTrainStatusResponse]:
        """Return live status for a train number, plus timetable origin/destination."""
        train_no = request.train_no.strip()
        try:
            if not train_no:
                raise exceptions.ValidationError("train_no is empty")
            live_map = await self._client.fetch_all()
            status_text = live_map.get(train_no)
            found = status_text is not None
            timetable = await self._repo.get_train_by_number(train_no)
            data = schemas.LiveTrainStatusResponse(
                train_no=train_no,
                found=found,
                status=status_text
                or "No live update for this train right now",
                origin=None if timetable is None else timetable.get("origin"),
                destination=None if timetable is None else timetable.get("destination"),
                line_code=None if timetable is None else timetable.get("line_code"),
            )
            logger.bind(train_no=train_no, found=found).info("live status ok")
            return schemas.APIResponse(data=data)
        except exceptions.AppError as exc:
            logger.bind(train_no=train_no, code=exc.code, error=exc.message).warning(
                "live status failed"
            )
            return schemas.APIResponse(
                error=schemas.ErrorDetail(code=exc.code, message=exc.message)
            )

    async def aclose(self) -> None:
        """Close the live-trains HTTP client."""
        await self._client.aclose()
