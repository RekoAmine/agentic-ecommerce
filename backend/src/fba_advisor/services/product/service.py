"""Product business service implemented through injected ports."""

from fba_advisor.domain.models import Product
from fba_advisor.ports.catalog import ProductAnalytics, ProductCatalog
from fba_advisor.ports.repositories import ProductRepository


class ProductResearchService:
    """Search and enrich product candidates without knowing external APIs."""

    def __init__(
        self,
        catalog: ProductCatalog,
        analytics: ProductAnalytics | None = None,
        repository: ProductRepository | None = None,
    ) -> None:
        """Inject product dependencies as interfaces."""
        self._catalog = catalog
        self._analytics = analytics
        self._repository = repository

    def search(self, query: str) -> list[Product]:
        """Return product candidates, optionally enriched through an analytics port."""
        normalized_query = query.strip()
        if not normalized_query:
            return []
        products = self._catalog.search(normalized_query)
        if self._analytics is not None:
            products = [self._analytics.enrich(product) for product in products]
        if self._repository is None:
            return products
        return [self._repository.save(product) for product in products]
