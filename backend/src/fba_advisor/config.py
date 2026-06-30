"""Runtime configuration for the backend service."""

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True, slots=True)
class BackendSettings:
    """Typed backend settings loaded from environment variables."""

    app_env: str = getenv("APP_ENV", "local")
    log_level: str = getenv("LOG_LEVEL", "INFO")
    database_url: str = getenv(
        "DATABASE_URL",
        "postgresql://agentic_ecommerce:change_me@postgres:5432/agentic_ecommerce",
    )
