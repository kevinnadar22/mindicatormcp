"""Read-only SQLite access for Mindicator data."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from loguru import logger

from app.core import exceptions


class MindicatorRepository:
    """Database access layer; only this class talks to SQLite."""

    def __init__(self, db_path: Path) -> None:
        """Store path to the SQLite file."""
        self._db_path = db_path.resolve()

    def _connect(self) -> sqlite3.Connection:
        """Open a read-only SQLite connection."""
        if not self._db_path.exists():
            raise exceptions.DatabaseError(f"database not found: {self._db_path}")
        uri = self._db_path.as_uri() + "?mode=ro"
        try:
            conn = sqlite3.connect(uri, uri=True, timeout=5.0)
        except sqlite3.Error as exc:
            raise exceptions.DatabaseError(str(exc)) from exc
        conn.row_factory = sqlite3.Row
        return conn

    def get_meta(self) -> dict[str, str]:
        """Return key/value pairs from the meta table."""
        logger.bind(table="meta").debug("fetching meta")
        with self._connect() as conn:
            rows = conn.execute("SELECT key, value FROM meta").fetchall()
        return {str(r["key"]): str(r["value"]) for r in rows}

    def list_user_tables(self) -> list[str]:
        """List user tables, excluding sqlite internal tables."""
        sql = (
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        )
        with self._connect() as conn:
            rows = conn.execute(sql).fetchall()
        return [str(r["name"]) for r in rows]

    def get_columns(self, table_name: str) -> list[dict[str, Any]]:
        """Return column metadata for one table via PRAGMA table_info."""
        with self._connect() as conn:
            rows = conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
        return [
            {
                "name": str(r["name"]),
                "type": str(r["type"] or "TEXT"),
                "notnull": bool(r["notnull"]),
                "pk": bool(r["pk"]),
            }
            for r in rows
        ]

    def count_rows(self, table_name: str) -> int:
        """Return row count for one table."""
        with self._connect() as conn:
            row = conn.execute(f'SELECT COUNT(*) AS c FROM "{table_name}"').fetchone()
        return int(row["c"]) if row else 0

    def fetch_all(self, sql: str) -> tuple[list[str], list[list[Any]]]:
        """Execute a read-only query and return columns plus rows."""
        logger.bind(sql=sql).debug("executing sql")
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql)
                columns = [d[0] for d in cursor.description] if cursor.description else []
                rows = [[_json_safe(v) for v in row] for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            logger.bind(sql=sql, error=str(exc)).error("sql failed")
            raise exceptions.DatabaseError(str(exc)) from exc
        return columns, rows


def _json_safe(value: Any) -> Any:
    """Coerce SQLite values into JSON-friendly Python types."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)
