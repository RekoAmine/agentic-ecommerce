"""Application use cases consumed by MCP product tools.

This module keeps business orchestration in the backend layer. Protocol adapters
(MCP, HTTP, CLIs) should call these use cases instead of implementing product
selection rules themselves.
"""

import logging
from collections.abc import Mapping
from contextlib import AbstractContextManager
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from fba_advisor.domain.models import MarginInput, Product, ProductScoreInput
from fba_advisor.ports.tracing import Tracer
from fba_advisor.services.margin import MarginService
from fba_advisor.services.product import ProductResearchService
from fba_advisor.services.score import ScoreService

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ProductToolUseCases:
    """Facade orchestrating product search, analysis, scoring, and margin use cases."""

    products: ProductResearchService
    margins: MarginService
    scores: ScoreService
    tracer: Tracer | None = None

    def search_products(self, query: str, limit: int) -> list[Product]:
        """Search product candidates through services, repositories, and connectors."""
        with self._span("product.search", {"query": query, "limit": limit}):
            products = self.products.search(query)[:limit]
            logger.info("product.search.completed", extra={"count": len(products)})
            return products

    def analyse_product(self, asin: str, marketplace: str) -> Mapping[str, object]:
        """Analyse a product from normalized persisted or provider-enriched signals."""
        with self._span("product.analyse", {"asin": asin, "marketplace": marketplace}):
            products = self.products.search(asin)
            product = next(
                (candidate for candidate in products if candidate.identifier == asin), None
            )
            if product is None and products:
                product = products[0]
            rank = product.sales_rank if product else None
            demand_level = "high" if rank is not None and rank <= 1_000 else "medium"
            competition_level = (
                "high"
                if product and _int_attribute(product.attributes.get("review_count")) > 500
                else "medium"
            )
            risk_level = "controlled" if product and product.price is not None else "needs_data"
            return {
                "asin": asin,
                "demand_level": demand_level,
                "competition_level": competition_level,
                "risk_level": risk_level,
                "opportunities": ("Validate differentiated positioning", "Compare supplier quotes"),
                "warnings": ("Confirm live fees before buying inventory",),
            }

    def calculate_margin(
        self,
        sale_price: Decimal,
        landed_cost: Decimal,
        amazon_fees: Decimal,
        fulfillment_cost: Decimal,
    ) -> Mapping[str, Decimal]:
        """Calculate FBA margin by delegating to the margin service."""
        with self._span("product.margin", {"sale_price": str(sale_price)}):
            estimate = self.margins.estimate(
                MarginInput(
                    selling_price=float(sale_price),
                    product_cost=float(landed_cost),
                    fulfillment_fee=float(fulfillment_cost),
                    referral_fee_rate=float(amazon_fees / sale_price),
                )
            )
            cents = Decimal("0.01")
            return {
                "sale_price": sale_price,
                "landed_cost": landed_cost,
                "amazon_fees": amazon_fees,
                "fulfillment_cost": fulfillment_cost,
                "net_profit": Decimal(str(estimate.profit)).quantize(cents, rounding=ROUND_HALF_UP),
                "margin_percent": (Decimal(str(estimate.margin_rate)) * Decimal("100")).quantize(
                    cents, rounding=ROUND_HALF_UP
                ),
            }

    def score_product(
        self, asin: str, monthly_sales_estimate: int, review_count: int, margin_percent: Decimal
    ) -> Mapping[str, object]:
        """Score a product by delegating normalized criteria to the score service."""
        with self._span("product.score", {"asin": asin}):
            score = self.scores.calculate(
                ProductScoreInput(
                    demand_score=min(monthly_sales_estimate / 1000, 1),
                    competition_score=min(review_count / 1000, 1),
                    margin_rate=min(float(margin_percent) / 100, 1),
                    supplier_reliability=0.5,
                    review_sentiment=0.5,
                ),
                product_identifier=asin,
            )
            recommendation = "investigate" if score.value >= 60 else "watchlist"
            return {
                "asin": asin,
                "score": max(1, round(score.value)),
                "recommendation": recommendation,
                "rationale": (score.rationale,),
            }

    def _span(self, name: str, attributes: Mapping[str, object]) -> AbstractContextManager[Any]:
        if self.tracer is None:
            from contextlib import nullcontext

            return nullcontext()
        return self.tracer.start_span(name, attributes)


def _int_attribute(value: object) -> int:
    """Safely coerce an arbitrary product attribute to an integer."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int | float | str | bytes | bytearray):
        return int(value)
    return 0
