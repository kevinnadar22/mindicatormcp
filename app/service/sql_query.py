"""Read-only SQL query service."""

from loguru import logger

from app.core import config, exceptions
from app.domain import schemas
from app.repository import MindicatorRepository
from app.utils import sql_safety


class SqlQueryService:
    """Validates and executes read-only SQL."""

    def __init__(self, repo: MindicatorRepository) -> None:
        """Bind the repository used for query execution."""
        self._repo = repo

    def execute(
        self, request: schemas.ExecuteSqlRequest
    ) -> schemas.APIResponse[schemas.SqlQueryResponse]:
        """Validate SQL, run it, and wrap the result set."""
        try:
            safe_sql = sql_safety.validate_and_limit(
                request.sql, config.settings.sql_row_limit
            )
            columns, rows = self._repo.fetch_all(safe_sql)
            truncated = len(rows) >= config.settings.sql_row_limit
            data = schemas.SqlQueryResponse(
                columns=columns,
                rows=rows,
                row_count=len(rows),
                truncated=truncated,
                sql_executed=safe_sql,
            )
            logger.bind(row_count=data.row_count, truncated=truncated).info("sql ok")
            return schemas.APIResponse(data=data)
        except exceptions.AppError as exc:
            logger.bind(code=exc.code, error=exc.message, sql=request.sql).warning(
                "sql rejected or failed"
            )
            return schemas.APIResponse(
                error=schemas.ErrorDetail(code=exc.code, message=exc.message)
            )
