"""Typed models for Amazon connector payloads."""

from pydantic import BaseModel, ConfigDict, Field


class AmazonCredentials(BaseModel):
    """Credentials required to call Amazon APIs."""

    access_key: str
    secret_key: str
    region: str
    marketplace_id: str


class AmazonProduct(BaseModel):
    """Provider-neutral representation of a product parsed from Amazon."""

    model_config = ConfigDict(frozen=True)

    asin: str
    title: str
    marketplace_id: str
    price: float | None = None
    currency: str | None = None
    raw: dict[str, object] = Field(default_factory=dict)


class AmazonSearchResponse(BaseModel):
    """Parsed Amazon product-search response."""

    products: list[AmazonProduct]
