"""Shared dependencies for MCP tool adapters."""

from fba_advisor.application.product_tools import ProductToolUseCases
from fba_advisor.connectors.amazon.models import AmazonProduct, AmazonSearchResponse
from fba_advisor.connectors.keepa.models import KeepaProduct, KeepaResponse
from fba_advisor.infrastructure.tracing import LoggingTracer
from fba_advisor.repositories.connectors import AmazonProductCatalog, KeepaProductAnalytics
from fba_advisor.services.margin import MarginService
from fba_advisor.services.product import ProductResearchService as BackendProductService
from fba_advisor.services.score import ScoreService
from fba_mcp_server.interfaces.product_service import ProductResearchService
from fba_mcp_server.services.product_research import BackendProductResearchService


class LocalAmazonConnector:
    """Local connector adapter used when no external Amazon credentials are configured."""

    provider_name = "amazon"

    def search_products(self, query: str) -> AmazonSearchResponse:
        """Return connector-shaped product data for local development and tests."""
        return AmazonSearchResponse(
            products=[
                AmazonProduct(
                    asin="B0TEST0001",
                    title=f"{query.title()} Starter Kit",
                    marketplace_id="ATVPDKIKX0DER",
                    price=29.99,
                    currency="USD",
                    raw={"monthly_sales_estimate": 840, "review_count": 128, "rating": 4.4},
                ),
                AmazonProduct(
                    asin="B0TEST0002",
                    title=f"Premium {query.title()} Bundle",
                    marketplace_id="ATVPDKIKX0DER",
                    price=44.90,
                    currency="USD",
                    raw={"monthly_sales_estimate": 520, "review_count": 76, "rating": 4.6},
                ),
            ]
        )


class LocalKeepaConnector:
    """Local analytics connector used when no external Keepa credentials are configured."""

    provider_name = "keepa"

    def fetch(self, value: str) -> KeepaResponse:
        """Return connector-shaped analytics for one ASIN."""
        return KeepaResponse(items=[KeepaProduct(asin=value, sales_rank=900, raw={})])


def get_product_research_service() -> ProductResearchService:
    """Build the product research service dependency graph."""
    catalog = AmazonProductCatalog(LocalAmazonConnector())
    analytics = KeepaProductAnalytics(LocalKeepaConnector())
    backend_products = BackendProductService(catalog, analytics)
    use_cases = ProductToolUseCases(
        products=backend_products,
        margins=MarginService(),
        scores=ScoreService(),
        tracer=LoggingTracer(),
    )
    return BackendProductResearchService(use_cases)
