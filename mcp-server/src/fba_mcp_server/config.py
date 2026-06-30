"""Runtime configuration for the MCP server."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class McpServerSettings(BaseSettings):
    """Typed MCP server settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)

    app_env: str = Field(default="local", validation_alias="APP_ENV")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    backend_base_url: str = Field(
        default="http://backend:8000", validation_alias="BACKEND_BASE_URL"
    )
    server_name: str = Field(default="agentic-ecommerce-mcp", validation_alias="MCP_SERVER_NAME")


def get_settings() -> McpServerSettings:
    """Return validated MCP server settings."""
    return McpServerSettings()
