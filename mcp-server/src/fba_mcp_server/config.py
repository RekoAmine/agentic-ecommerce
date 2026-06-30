"""Runtime configuration for the MCP server."""

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True, slots=True)
class McpServerSettings:
    """Typed MCP server settings loaded from environment variables."""

    app_env: str = getenv("APP_ENV", "local")
    log_level: str = getenv("LOG_LEVEL", "INFO")
    backend_base_url: str = getenv("BACKEND_BASE_URL", "http://backend:8000")
