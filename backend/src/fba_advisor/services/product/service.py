"""Product business service implemented through injected ports."""

from fba_advisor.domain.models import Product
from fba_advisor.ports.catalog import ProductAnalytics, ProductCatalog


class ProductResearchService:
    """Search and enrich product candidates without knowing external APIs."""

    def __init__(self, catalog: ProductCatalog, analytics: ProductAnalytics | None = None) -> None:
        """Inject product data dependencies as interfaces."""
        self._catalog = catalog
        self._analytics = analytics

    def search(self, query: str) -> list[Product]:
        """Return product candidates, optionally enriched through an analytics port."""
        normalized_query = query.strip()
        if not normalized_query:
            return []
        products = self._catalog.search(normalized_query)
        if self._analytics is None:
            return products
        return [self._analytics.enrich(product) for product in products]
