"""Repository/adapters that translate connector models into domain models."""

from fba_advisor.connectors.amazon.interfaces import AmazonConnector
from fba_advisor.connectors.keepa.interfaces import KeepaConnector
from fba_advisor.domain.models import Product
from fba_advisor.ports.catalog import ProductAnalytics, ProductCatalog


class AmazonProductCatalog(ProductCatalog):
    """Product catalog repository backed by the Amazon connector."""

    def __init__(self, connector: AmazonConnector) -> None:
        """Create the catalog with an injected connector."""
        self._connector = connector

    def search(self, query: str) -> list[Product]:
        """Search Amazon and map results to domain products."""
        response = self._connector.search_products(query)
        return [
            Product(
                identifier=item.asin,
                title=item.title,
                source=self._connector.provider_name,
                price=item.price,
                currency=item.currency,
                attributes={"marketplace_id": item.marketplace_id, "raw": item.raw},
            )
            for item in response.products
        ]


class KeepaProductAnalytics(ProductAnalytics):
    """Product analytics repository backed by the Keepa connector."""

    def __init__(self, connector: KeepaConnector) -> None:
        """Create the analytics adapter with an injected connector."""
        self._connector = connector

    def enrich(self, product: Product) -> Product:
        """Fetch Keepa metrics and merge them with an existing product."""
        response = self._connector.fetch(product.identifier)
        item = next(
            (candidate for candidate in response.items if candidate.asin == product.identifier),
            None,
        )
        if item is None:
            return product
        attributes = dict(product.attributes)
        attributes["keepa"] = item.raw
        return Product(
            identifier=product.identifier,
            title=item.title or product.title,
            source=product.source,
            price=product.price,
            currency=product.currency,
            sales_rank=item.sales_rank,
            attributes=attributes,
        )
