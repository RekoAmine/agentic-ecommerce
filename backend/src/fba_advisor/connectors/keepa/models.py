"""Typed models for Keepa connector payloads."""

from pydantic import BaseModel, ConfigDict, Field


class KeepaCredentials(BaseModel):
    """Credentials required to call Keepa APIs."""

    api_key: str


class KeepaProduct(BaseModel):
    """Parsed Keepa data returned by the connector."""

    model_config = ConfigDict(frozen=True)

    asin: str
    title: str | None = None
    sales_rank: int | None = None
    raw: dict[str, object] = Field(default_factory=dict)


class KeepaResponse(BaseModel):
    """Parsed Keepa response."""

    items: list[KeepaProduct]
