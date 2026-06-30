"""Keepa API client focused on authentication, API calls, and parsing."""

import json
from collections.abc import Mapping
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fba_advisor.connectors.keepa.exceptions import KeepaAPIError, KeepaParsingError
from fba_advisor.connectors.keepa.mapper import map_response
from fba_advisor.connectors.keepa.models import KeepaCredentials, KeepaResponse


class KeepaTransport(Protocol):
    """Minimal transport contract used to keep the connector replaceable in tests."""

    def get(self, url: str, headers: Mapping[str, str]) -> tuple[int, bytes]:
        """Perform an HTTP GET request."""
        ...


class UrllibKeepaTransport:
    """urllib-based Keepa HTTP transport."""

    def get(self, url: str, headers: Mapping[str, str]) -> tuple[int, bytes]:
        """Perform an HTTP GET request using the standard library."""
        request = Request(url, headers=dict(headers), method="GET")
        with urlopen(request, timeout=30) as response:  # noqa: S310
            return response.status, response.read()


class KeepaClient:
    """Keepa connector client."""

    provider_name = "keepa"

    def __init__(
        self, credentials: KeepaCredentials, base_url: str, transport: KeepaTransport | None = None
    ) -> None:
        """Initialize the client with credentials, base URL, and optional transport."""
        self._credentials = credentials
        self._base_url = base_url.rstrip("/")
        self._transport = transport or UrllibKeepaTransport()

    def fetch(self, value: str) -> KeepaResponse:
        """Fetch product data and return parsed Keepa connector models."""
        params = urlencode({"key": self._credentials.api_key, "asin": value})
        status, body = self._transport.get(
            f"{self._base_url}/product?{params}", {"Accept": "application/json"}
        )
        if status >= 400:
            raise KeepaAPIError(f"Keepa API returned status {status}.")
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise KeepaParsingError("Keepa API returned invalid JSON.") from exc
        if not isinstance(payload, dict):
            raise KeepaParsingError("Keepa API response must be a JSON object.")
        return map_response(payload)
