"""OpenAI API client focused on authentication, API calls, and parsing."""

import json
from collections.abc import Mapping
from typing import Protocol
from urllib.request import Request, urlopen

from fba_advisor.connectors.openai.exceptions import OpenAIAPIError, OpenAIParsingError
from fba_advisor.connectors.openai.mapper import map_response
from fba_advisor.connectors.openai.models import OpenAICredentials, OpenAIResponse


class OpenAITransport(Protocol):
    """Minimal transport contract used to keep the connector replaceable in tests."""

    def post(self, url: str, headers: Mapping[str, str], body: bytes) -> tuple[int, bytes]:
        """Perform an HTTP POST request."""
        ...


class UrllibOpenAITransport:
    """urllib-based OpenAI HTTP transport."""

    def post(self, url: str, headers: Mapping[str, str], body: bytes) -> tuple[int, bytes]:
        """Perform an HTTP POST request using the standard library."""
        request = Request(url, data=body, headers=dict(headers), method="POST")
        with urlopen(request, timeout=30) as response:  # noqa: S310
            return response.status, response.read()


class OpenAIClient:
    """OpenAI connector client."""

    provider_name = "openai"

    def __init__(
        self,
        credentials: OpenAICredentials,
        base_url: str,
        model: str,
        transport: OpenAITransport | None = None,
    ) -> None:
        """Initialize the client with credentials, base URL, model, and optional transport."""
        self._credentials = credentials
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._transport = transport or UrllibOpenAITransport()

    def fetch(self, value: str) -> OpenAIResponse:
        """Fetch embeddings and return parsed OpenAI connector models."""
        body = json.dumps({"model": self._model, "input": value}).encode("utf-8")
        status, response_body = self._transport.post(
            f"{self._base_url}/embeddings", self._headers(), body
        )
        if status >= 400:
            raise OpenAIAPIError(f"OpenAI API returned status {status}.")
        try:
            payload = json.loads(response_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise OpenAIParsingError("OpenAI API returned invalid JSON.") from exc
        if not isinstance(payload, dict):
            raise OpenAIParsingError("OpenAI API response must be a JSON object.")
        return map_response(payload, value, self._model)

    def _headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._credentials.api_key}",
            "Content-Type": "application/json",
        }
        if self._credentials.organization:
            headers["OpenAI-Organization"] = self._credentials.organization
        return headers
