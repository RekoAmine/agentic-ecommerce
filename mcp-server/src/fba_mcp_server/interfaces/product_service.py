"""Ports for product-oriented application services."""

from decimal import Decimal
from typing import Protocol

from fba_mcp_server.schemas.products import (
    MarginBreakdown,
    ProductAnalysis,
    ProductScore,
    ProductSummary,
)
from fba_mcp_server.schemas.requests import (
    AnalyseProductRequest,
    ScoreProductRequest,
    SearchProductsRequest,
)


class ProductResearchService(Protocol):
    """Application boundary used by MCP tools to research products."""

    def search_products(self, request: SearchProductsRequest) -> list[ProductSummary]:
        """Search products matching the request."""
        ...

    def analyse_product(self, request: AnalyseProductRequest) -> ProductAnalysis:
        """Analyse a product."""
        ...

    def calculate_margin(
        self,
        sale_price: Decimal,
        landed_cost: Decimal,
        amazon_fees: Decimal,
        fulfillment_cost: Decimal,
    ) -> MarginBreakdown:
        """Calculate product margin."""
        ...

    def score_product(self, request: ScoreProductRequest) -> ProductScore:
        """Score a product opportunity."""
        ...
