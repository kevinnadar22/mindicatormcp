"""SQL safety helpers for read-only queries."""

from __future__ import annotations

import re

from loguru import logger

from app.core import exceptions

_FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|ATTACH|DETACH|CREATE|REPLACE|PRAGMA|VACUUM|"
    r"GRANT|REVOKE|TRUNCATE|INTO)\b",
    re.IGNORECASE,
)
_LIMIT = re.compile(r"\bLIMIT\s+(\d+)\b", re.IGNORECASE)
_COMMENT_LINE = re.compile(r"--.*?$", re.MULTILINE)
_COMMENT_BLOCK = re.compile(r"/\*.*?\*/", re.DOTALL)


def validate_and_limit(sql: str, max_limit: int) -> str:
    """Validate read-only SQL and ensure a capped LIMIT clause."""
    cleaned = _COMMENT_BLOCK.sub(" ", _COMMENT_LINE.sub(" ", sql)).strip().rstrip(";")
    if not cleaned:
        raise exceptions.SqlSafetyError("SQL is empty")
    if ";" in cleaned:
        raise exceptions.SqlSafetyError("multiple statements are not allowed")

    upper = cleaned.lstrip().upper()
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        raise exceptions.SqlSafetyError("only SELECT or WITH statements are allowed")
    if _FORBIDDEN.search(cleaned):
        raise exceptions.SqlSafetyError("statement contains forbidden keywords")

    match = _LIMIT.search(cleaned)
    if match:
        limit = min(int(match.group(1)), max_limit)
        cleaned = _LIMIT.sub(f"LIMIT {limit}", cleaned, count=1)
    else:
        cleaned = f"{cleaned} LIMIT {max_limit}"

    logger.bind(sql=cleaned, max_limit=max_limit).debug("sql validated")
    return cleaned
