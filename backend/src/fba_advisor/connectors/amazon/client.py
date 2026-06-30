"""Amazon API client focused on authentication, API calls, and parsing."""

import json
from collections.abc import Mapping
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fba_advisor.connectors.amazon.exceptions import AmazonAPIError, AmazonParsingError
from fba_advisor.connectors.amazon.mapper import map_search_response
from fba_advisor.connectors.amazon.models import AmazonCredentials, AmazonSearchResponse


class AmazonTransport(Protocol):
    """Minimal transport contract used to keep the connector replaceable in tests."""

    def get(self, url: str, headers: Mapping[str, str]) -> tuple[int, bytes]:
        """Perform an HTTP GET request."""
        ...


class UrllibAmazonTransport:
    """urllib-based Amazon HTTP transport."""

    def get(self, url: str, headers: Mapping[str, str]) -> tuple[int, bytes]:
        """Perform an HTTP GET request using the standard library."""
        request = Request(url, headers=dict(headers), method="GET")
        with urlopen(request, timeout=30) as response:  # noqa: S310
            return response.status, response.read()


class AmazonClient:
    """Amazon connector client."""

    provider_name = "amazon"

    def __init__(
        self,
        credentials: AmazonCredentials,
        base_url: str,
        transport: AmazonTransport | None = None,
    ) -> None:
        """Initialize the client with credentials, base URL, and optional transport."""
        self._credentials = credentials
        self._base_url = base_url.rstrip("/")
        self._transport = transport or UrllibAmazonTransport()

    def search_products(self, query: str) -> AmazonSearchResponse:
        """Search products and return parsed Amazon connector models."""
        params = urlencode({"q": query, "marketplace_id": self._credentials.marketplace_id})
        status, body = self._transport.get(
            f"{self._base_url}/products/search?{params}", self._headers()
        )
        if status >= 400:
            msg = f"Amazon API returned status {status}."
            raise AmazonAPIError(msg)
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            msg = "Amazon API returned invalid JSON."
            raise AmazonParsingError(msg) from exc
        if not isinstance(payload, dict):
            msg = "Amazon API response must be a JSON object."
            raise AmazonParsingError(msg)
        return map_search_response(payload, self._credentials.marketplace_id)

    def _headers(self) -> dict[str, str]:
        authorization = f"Amazon {self._credentials.access_key}:{self._credentials.secret_key}"
        return {
            "Authorization": authorization,
            "X-Amz-Region": self._credentials.region,
            "Accept": "application/json",
        }
