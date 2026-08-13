"""HTTP client for the Mobond live-train tracker."""

from __future__ import annotations

import json

import httpx
from loguru import logger

from app.core import config, exceptions


class LiveTrainsClient:
    """Fetches the live train map from Mobond over async HTTP."""

    def __init__(self) -> None:
        """Defer client creation until the first request on the running loop."""
        self._http: httpx.AsyncClient | None = None

    def _client(self) -> httpx.AsyncClient:
        """Return a shared AsyncClient, creating it if needed."""
        if self._http is None or self._http.is_closed:
            timeout_s = config.settings.live_trains_timeout_ms / 1000
            self._http = httpx.AsyncClient(
                timeout=timeout_s,
                headers={
                    "User-Agent": "mindicator-mcp/0.1",
                    "Accept": "application/json",
                },
            )
        return self._http

    async def fetch_all(self) -> dict[str, str]:
        """Return train_no → status text for currently tracked trains."""
        url = config.settings.live_trains_url
        logger.bind(url=url).info("fetching live trains")
        try:
            response = await self._client().get(url)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, json.JSONDecodeError) as exc:
            logger.bind(url=url, error=str(exc)).error("live trains fetch failed")
            raise exceptions.IntegrationError(
                f"live trains feed unavailable: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise exceptions.IntegrationError("live trains feed returned unexpected JSON")
        return {str(k): str(v) for k, v in payload.items()}

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        if self._http is not None:
            await self._http.aclose()
            self._http = None
