"""MCP-facing product research adapter.

The adapter contains no business rules: it validates MCP schemas, delegates to
backend application use cases, and maps backend DTOs back to MCP schemas.
"""

from decimal import Decimal
from typing import Any, cast

from fba_advisor.application.product_tools import ProductToolUseCases
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


class BackendProductResearchService:
    """Adapter from MCP tool contracts to backend application use cases."""

    def __init__(self, use_cases: ProductToolUseCases) -> None:
        """Create the adapter with injected backend use cases."""
        self._use_cases = use_cases

    def search_products(self, request: SearchProductsRequest) -> list[ProductSummary]:
        """Delegate product search to backend use cases."""
        products = self._use_cases.search_products(request.query, request.limit)
        summaries: list[ProductSummary] = []
        for product in products:
            raw = product.attributes.get("raw", {})
            raw_data = raw if isinstance(raw, dict) else {}
            summaries.append(
                ProductSummary(
                    asin=product.identifier,
                    title=product.title,
                    marketplace=request.marketplace,
                    price=Decimal(str(product.price or 0)).quantize(Decimal("0.01")),
                    currency=product.currency or "USD",
                    monthly_sales_estimate=int(raw_data.get("monthly_sales_estimate", 0)),
                    review_count=int(raw_data.get("review_count", 0)),
                    rating=float(raw_data.get("rating", 0)),
                    product_url=cast(Any, f"https://www.amazon.com/dp/{product.identifier}"),
                )
            )
        return summaries

    def analyse_product(self, request: AnalyseProductRequest) -> ProductAnalysis:
        """Delegate product analysis to backend use cases."""
        data = self._use_cases.analyse_product(request.asin, request.marketplace.value)
        return ProductAnalysis(**cast(dict[str, Any], data))

    def calculate_margin(
        self,
        sale_price: Decimal,
        landed_cost: Decimal,
        amazon_fees: Decimal,
        fulfillment_cost: Decimal,
    ) -> MarginBreakdown:
        """Delegate margin calculation to backend use cases."""
        return MarginBreakdown(
            **self._use_cases.calculate_margin(
                sale_price, landed_cost, amazon_fees, fulfillment_cost
            )
        )

    def score_product(self, request: ScoreProductRequest) -> ProductScore:
        """Delegate product scoring to backend use cases."""
        score_data = self._use_cases.score_product(
            request.asin,
            request.monthly_sales_estimate,
            request.review_count,
            request.margin_percent,
        )
        return ProductScore(**cast(dict[str, Any], score_data))
