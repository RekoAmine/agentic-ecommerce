"""Pydantic data models shared by MCP product tools."""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, NonNegativeInt, PositiveInt


class Marketplace(StrEnum):
    """Supported marketplace identifiers."""

    AMAZON_US = "amazon_us"
    AMAZON_FR = "amazon_fr"
    AMAZON_DE = "amazon_de"
    AMAZON_UK = "amazon_uk"


class ProductSummary(BaseModel):
    """Search result returned by product discovery providers."""

    model_config = ConfigDict(frozen=True)

    asin: str = Field(..., min_length=10, max_length=10)
    title: str = Field(..., min_length=1)
    marketplace: Marketplace
    price: Decimal = Field(..., ge=Decimal("0"), max_digits=10, decimal_places=2)
    currency: str = Field(..., min_length=3, max_length=3)
    monthly_sales_estimate: NonNegativeInt
    review_count: NonNegativeInt
    rating: float = Field(..., ge=0, le=5)
    product_url: HttpUrl


class ProductAnalysis(BaseModel):
    """Structured analysis for a single catalog product."""

    model_config = ConfigDict(frozen=True)

    asin: str = Field(..., min_length=10, max_length=10)
    demand_level: str = Field(..., min_length=1)
    competition_level: str = Field(..., min_length=1)
    risk_level: str = Field(..., min_length=1)
    opportunities: tuple[str, ...]
    warnings: tuple[str, ...]


class MarginBreakdown(BaseModel):
    """Financial margin details for a potential FBA product."""

    model_config = ConfigDict(frozen=True)

    sale_price: Decimal = Field(..., ge=Decimal("0"), max_digits=10, decimal_places=2)
    landed_cost: Decimal = Field(..., ge=Decimal("0"), max_digits=10, decimal_places=2)
    amazon_fees: Decimal = Field(..., ge=Decimal("0"), max_digits=10, decimal_places=2)
    fulfillment_cost: Decimal = Field(..., ge=Decimal("0"), max_digits=10, decimal_places=2)
    net_profit: Decimal = Field(..., max_digits=10, decimal_places=2)
    margin_percent: Decimal = Field(..., max_digits=5, decimal_places=2)


class ProductScore(BaseModel):
    """Decision score for product selection."""

    model_config = ConfigDict(frozen=True)

    asin: str = Field(..., min_length=10, max_length=10)
    score: PositiveInt = Field(..., le=100)
    recommendation: str = Field(..., min_length=1)
    rationale: tuple[str, ...]
