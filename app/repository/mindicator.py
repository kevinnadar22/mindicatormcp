"""Read-only SQLite access for Mindicator data."""

from __future__ import annotations

import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import aiosqlite
from loguru import logger

from app.core import exceptions


class MindicatorRepository:
    """Database access layer; only this class talks to SQLite."""

    def __init__(self, db_path: Path) -> None:
        """Store path to the SQLite file."""
        self._db_path = db_path.resolve()

    @asynccontextmanager
    async def _connect(self) -> AsyncIterator[aiosqlite.Connection]:
        """Yield a read-only SQLite connection."""
        if not self._db_path.exists():
            raise exceptions.DatabaseError(f"database not found: {self._db_path}")
        try:
            async with aiosqlite.connect(
                self._db_path.as_uri() + "?mode=ro",
                uri=True,
                timeout=5.0,
            ) as conn:
                conn.row_factory = aiosqlite.Row
                yield conn
        except sqlite3.Error as exc:
            raise exceptions.DatabaseError(str(exc)) from exc

    async def get_meta(self) -> dict[str, str]:
        """Return key/value pairs from the meta table."""
        logger.bind(table="meta").debug("fetching meta")
        async with self._connect() as conn:
            cursor = await conn.execute("SELECT key, value FROM meta")
            rows = await cursor.fetchall()
        return {str(r["key"]): str(r["value"]) for r in rows}

    async def list_user_tables(self) -> list[str]:
        """List user tables, excluding sqlite internal tables."""
        sql = (
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        )
        async with self._connect() as conn:
            cursor = await conn.execute(sql)
            rows = await cursor.fetchall()
        return [str(r["name"]) for r in rows]

    async def get_columns(self, table_name: str) -> list[dict[str, Any]]:
        """Return column metadata for one table via PRAGMA table_info."""
        async with self._connect() as conn:
            cursor = await conn.execute(f'PRAGMA table_info("{table_name}")')
            rows = await cursor.fetchall()
        return [
            {
                "name": str(r["name"]),
                "type": str(r["type"] or "TEXT"),
                "notnull": bool(r["notnull"]),
                "pk": bool(r["pk"]),
            }
            for r in rows
        ]

    async def count_rows(self, table_name: str) -> int:
        """Return row count for one table."""
        async with self._connect() as conn:
            cursor = await conn.execute(f'SELECT COUNT(*) AS c FROM "{table_name}"')
            row = await cursor.fetchone()
        return int(row["c"]) if row else 0

    async def get_train_by_number(self, train_no: str) -> dict[str, Any] | None:
        """Return timetable fields for a train number, if present."""
        sql = (
            "SELECT train_no, origin, destination, line_code, service_class "
            "FROM trains WHERE train_no = ? LIMIT 1"
        )
        logger.bind(train_no=train_no).debug("looking up train")
        async with self._connect() as conn:
            cursor = await conn.execute(sql, (train_no,))
            row = await cursor.fetchone()
        if row is None:
            return None
        return {key: _json_safe(row[key]) for key in row.keys()}

    async def search_stations(self, query: str, limit: int) -> list[dict[str, Any]]:
        """Search stations by name fragment."""
        sql = (
            "SELECT name, lat, lon FROM stations "
            "WHERE UPPER(name) LIKE '%' || UPPER(?) || '%' "
            "ORDER BY name LIMIT ?"
        )
        return await self._fetch_dicts(sql, (query, limit))

    async def find_transfer_paths(
        self, from_station: str, to_station: str, limit: int
    ) -> list[dict[str, Any]]:
        """Find path hints between two stations."""
        sql = (
            "SELECT from_station, to_station, path_desc FROM transfer_paths "
            "WHERE UPPER(from_station) = UPPER(?) AND UPPER(to_station) = UPPER(?) "
            "LIMIT ?"
        )
        return await self._fetch_dicts(sql, (from_station, to_station, limit))

    async def find_ticket_fares(
        self, from_station: str, to_station: str, limit: int
    ) -> list[dict[str, Any]]:
        """Find ticket fare rows for an OD pair."""
        sql = (
            "SELECT src_station, dst_station, route_code, fare_1, fare_6 "
            "FROM ticket_fares "
            "WHERE UPPER(src_station) = UPPER(?) AND UPPER(dst_station) = UPPER(?) "
            "LIMIT ?"
        )
        return await self._fetch_dicts(sql, (from_station, to_station, limit))

    async def search_bus_routes(
        self, query: str, agency: str | None, limit: int
    ) -> list[dict[str, Any]]:
        """Search bus routes by code, optionally filtered by agency."""
        if agency:
            sql = (
                "SELECT agency, code, stop_count FROM bus_routes "
                "WHERE UPPER(agency) = UPPER(?) AND UPPER(code) LIKE '%' || UPPER(?) || '%' "
                "ORDER BY agency, code LIMIT ?"
            )
            return await self._fetch_dicts(sql, (agency, query, limit))
        sql = (
            "SELECT agency, code, stop_count FROM bus_routes "
            "WHERE UPPER(code) LIKE '%' || UPPER(?) || '%' "
            "ORDER BY agency, code LIMIT ?"
        )
        return await self._fetch_dicts(sql, (query, limit))

    async def get_bus_route_stops(
        self, agency: str, route_code: str, limit: int
    ) -> list[dict[str, Any]]:
        """Return ordered stops for one bus route."""
        sql = (
            "SELECT seq, stop_name, stop_index FROM bus_route_stops "
            "WHERE UPPER(agency) = UPPER(?) AND UPPER(route_code) = UPPER(?) "
            "ORDER BY seq LIMIT ?"
        )
        return await self._fetch_dicts(sql, (agency, route_code, limit))

    async def get_auto_fare_for_km(self, km: float) -> dict[str, Any] | None:
        """Return the closest auto fare row at or below the given km."""
        sql = (
            "SELECT km, fare, night_fare FROM auto_fares "
            "WHERE km <= ? ORDER BY km DESC LIMIT 1"
        )
        rows = await self._fetch_dicts(sql, (km,))
        return rows[0] if rows else None

    async def _fetch_dicts(
        self, sql: str, params: tuple[Any, ...]
    ) -> list[dict[str, Any]]:
        """Run a parameterized query and return JSON-safe dict rows."""
        logger.bind(sql=sql).debug("executing parameterized sql")
        try:
            async with self._connect() as conn:
                cursor = await conn.execute(sql, params)
                rows = await cursor.fetchall()
        except sqlite3.Error as exc:
            logger.bind(sql=sql, error=str(exc)).error("sql failed")
            raise exceptions.DatabaseError(str(exc)) from exc
        return [{key: _json_safe(row[key]) for key in row.keys()} for row in rows]

    async def fetch_all(self, sql: str) -> tuple[list[str], list[list[Any]]]:
        """Execute a read-only query and return columns plus rows."""
        logger.bind(sql=sql).debug("executing sql")
        try:
            async with self._connect() as conn:
                cursor = await conn.execute(sql)
                columns = [d[0] for d in cursor.description] if cursor.description else []
                rows = [[_json_safe(v) for v in row] for row in await cursor.fetchall()]
        except sqlite3.Error as exc:
            logger.bind(sql=sql, error=str(exc)).error("sql failed")
            raise exceptions.DatabaseError(str(exc)) from exc
        return columns, rows


def _json_safe(value: Any) -> Any:
    """Coerce SQLite values into JSON-friendly Python types."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)
