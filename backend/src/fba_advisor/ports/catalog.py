"""Business-facing catalog and sourcing ports."""

from typing import Protocol

from fba_advisor.domain.models import Product, Supplier


class ProductCatalog(Protocol):
    """Port for searching normalized product candidates."""

    def search(self, query: str) -> list[Product]:
        """Return normalized products for a query."""
        ...


class ProductAnalytics(Protocol):
    """Port for enriching product candidates with market analytics."""

    def enrich(self, product: Product) -> Product:
        """Return a product enriched with analytics data."""
        ...


class SupplierDirectory(Protocol):
    """Port for finding normalized supplier candidates."""

    def find(self, query: str) -> list[Supplier]:
        """Return normalized suppliers for a query."""
        ...
