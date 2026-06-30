"""Request models for MCP tools."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, PositiveInt

from fba_mcp_server.schemas.products import Marketplace


class SearchProductsRequest(BaseModel):
    """Validated input for product search."""

    model_config = ConfigDict(frozen=True)

    query: str = Field(..., min_length=2, max_length=120)
    marketplace: Marketplace = Marketplace.AMAZON_US
    limit: PositiveInt = Field(default=5, le=20)


class AnalyseProductRequest(BaseModel):
    """Validated input for product analysis."""

    model_config = ConfigDict(frozen=True)

    asin: str = Field(..., min_length=10, max_length=10)
    marketplace: Marketplace = Marketplace.AMAZON_US


class CalculateMarginRequest(BaseModel):
    """Validated input for FBA margin calculations."""

    model_config = ConfigDict(frozen=True)

    sale_price: Decimal = Field(..., gt=Decimal("0"), max_digits=10, decimal_places=2)
    landed_cost: Decimal = Field(..., ge=Decimal("0"), max_digits=10, decimal_places=2)
    amazon_fees: Decimal = Field(..., ge=Decimal("0"), max_digits=10, decimal_places=2)
    fulfillment_cost: Decimal = Field(..., ge=Decimal("0"), max_digits=10, decimal_places=2)


class ScoreProductRequest(BaseModel):
    """Validated input for product scoring."""

    model_config = ConfigDict(frozen=True)

    asin: str = Field(..., min_length=10, max_length=10)
    monthly_sales_estimate: NonNegativeInt
    review_count: NonNegativeInt
    margin_percent: Decimal = Field(..., max_digits=5, decimal_places=2)
