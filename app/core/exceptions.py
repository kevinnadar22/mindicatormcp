"""Application exception types."""


class AppError(Exception):
    """Base application error with a stable error code."""

    def __init__(self, message: str, code: str = "APP_ERROR") -> None:
        """Store message and machine-readable code."""
        super().__init__(message)
        self.message = message
        self.code = code


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str) -> None:
        """Create a not-found error."""
        super().__init__(message, code="NOT_FOUND")


class ValidationError(AppError):
    """Raised when input fails validation."""

    def __init__(self, message: str) -> None:
        """Create a validation error."""
        super().__init__(message, code="VALIDATION")


class SqlSafetyError(AppError):
    """Raised when SQL is rejected by safety checks."""

    def __init__(self, message: str) -> None:
        """Create a SQL safety error."""
        super().__init__(message, code="SQL_SAFETY")


class DatabaseError(AppError):
    """Raised when a database operation fails."""

    def __init__(self, message: str) -> None:
        """Create a database error."""
        super().__init__(message, code="DATABASE")
