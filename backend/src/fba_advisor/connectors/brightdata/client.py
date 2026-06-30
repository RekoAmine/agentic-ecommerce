"""Bright Data client focused on authentication, API calls, and parsing."""

import json
from collections.abc import Mapping
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fba_advisor.connectors.brightdata.exceptions import BrightDataAPIError, BrightDataParsingError
from fba_advisor.connectors.brightdata.mapper import map_response
from fba_advisor.connectors.brightdata.models import (
    BrightDataCredentials,
    BrightDataResponse,
    BrightDataTarget,
)


class BrightDataTransport(Protocol):
    """Minimal transport contract used to keep Bright Data replaceable in tests."""

    def get(self, url: str, headers: Mapping[str, str]) -> tuple[int, bytes]:
        """Perform an HTTP GET request."""
        ...


class UrllibBrightDataTransport:
    """urllib-based Bright Data HTTP transport."""

    def get(self, url: str, headers: Mapping[str, str]) -> tuple[int, bytes]:
        """Perform an HTTP GET request using the standard library."""
        request = Request(url, headers=dict(headers), method="GET")
        with urlopen(request, timeout=30) as response:  # noqa: S310
            return response.status, response.read()


class BrightDataClient:
    """Bright Data connector client for Amazon, Alibaba, and Google targets."""

    provider_name = "brightdata"

    def __init__(
        self,
        credentials: BrightDataCredentials,
        base_url: str,
        transport: BrightDataTransport | None = None,
    ) -> None:
        """Initialize the client with credentials, base URL, and optional transport."""
        self._credentials = credentials
        self._base_url = base_url.rstrip("/")
        self._transport = transport or UrllibBrightDataTransport()

    def collect(self, target: BrightDataTarget, query: str) -> BrightDataResponse:
        """Collect target data and return parsed Bright Data connector records."""
        params = {"target": target.value, "query": query}
        if self._credentials.zone:
            params["zone"] = self._credentials.zone
        status, body = self._transport.get(
            f"{self._base_url}/collect?{urlencode(params)}",
            {
                "Authorization": f"Bearer {self._credentials.api_token}",
                "Accept": "application/json",
            },
        )
        if status >= 400:
            msg = f"Bright Data API returned status {status}."
            raise BrightDataAPIError(msg)
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            msg = "Bright Data API returned invalid JSON."
            raise BrightDataParsingError(msg) from exc
        if not isinstance(payload, dict):
            msg = "Bright Data API response must be a JSON object."
            raise BrightDataParsingError(msg)
        return map_response(payload, target)
