"""Simulated product research service implementation."""

from decimal import ROUND_HALF_UP, Decimal

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


class SimulatedProductResearchService:
    """Deterministic fake service used until real provider adapters are connected."""

    def search_products(self, request: SearchProductsRequest) -> list[ProductSummary]:
        """Return deterministic simulated products respecting production schemas."""
        products = [
            ProductSummary(
                asin="B0TEST0001",
                title=f"{request.query.title()} Starter Kit",
                marketplace=request.marketplace,
                price=Decimal("29.99"),
                currency="USD",
                monthly_sales_estimate=840,
                review_count=128,
                rating=4.4,
                product_url="https://www.amazon.com/dp/B0TEST0001",
            ),
            ProductSummary(
                asin="B0TEST0002",
                title=f"Premium {request.query.title()} Bundle",
                marketplace=request.marketplace,
                price=Decimal("44.90"),
                currency="USD",
                monthly_sales_estimate=520,
                review_count=76,
                rating=4.6,
                product_url="https://www.amazon.com/dp/B0TEST0002",
            ),
        ]
        return products[: request.limit]

    def analyse_product(self, request: AnalyseProductRequest) -> ProductAnalysis:
        """Return a simulated product analysis."""
        return ProductAnalysis(
            asin=request.asin,
            demand_level="medium-high",
            competition_level="medium",
            risk_level="controlled",
            opportunities=("Bundle differentiation", "Keyword long-tail expansion"),
            warnings=("Validate supplier lead times", "Confirm FBA fee category"),
        )

    def calculate_margin(
        self,
        sale_price: Decimal,
        landed_cost: Decimal,
        amazon_fees: Decimal,
        fulfillment_cost: Decimal,
    ) -> MarginBreakdown:
        """Calculate a deterministic margin breakdown from validated inputs."""
        net_profit = sale_price - landed_cost - amazon_fees - fulfillment_cost
        margin_percent = (net_profit / sale_price * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return MarginBreakdown(
            sale_price=sale_price,
            landed_cost=landed_cost,
            amazon_fees=amazon_fees,
            fulfillment_cost=fulfillment_cost,
            net_profit=net_profit.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            margin_percent=margin_percent,
        )

    def score_product(self, request: ScoreProductRequest) -> ProductScore:
        """Return a simulated product score based on simple deterministic rules."""
        demand_points = min(request.monthly_sales_estimate // 20, 40)
        review_penalty = min(request.review_count // 50, 20)
        margin_points = max(min(int(request.margin_percent), 40), 0)
        score = max(min(demand_points + margin_points - review_penalty + 20, 100), 1)
        recommendation = "investigate" if score >= 70 else "watchlist"
        return ProductScore(
            asin=request.asin,
            score=score,
            recommendation=recommendation,
            rationale=(
                "Demand, competition, and margin were scored with simulated heuristics.",
                "Connect real marketplace and fee providers before production decisions.",
            ),
        )
