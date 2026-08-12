"""Shared API response envelope schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Machine-readable error payload."""

    code: str
    message: str


class APIResponse(BaseModel, Generic[T]):
    """Standard response wrapper for every MCP tool."""

    data: T | None = None
    error: ErrorDetail | None = None
