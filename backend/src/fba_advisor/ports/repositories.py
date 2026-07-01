"""Persistence ports consumed by services."""

from typing import Protocol

from fba_advisor.domain.models import (
    Product,
    ProductReview,
    ProductScore,
    ProductScoreInput,
    Supplier,
)


class ProductRepository(Protocol):
    """Port for storing products."""

    def save(self, product: Product) -> Product:
        """Persist and return a product."""
        ...


class SupplierRepository(Protocol):
    """Port for storing suppliers."""

    def save(self, supplier: Supplier) -> Supplier:
        """Persist and return a supplier."""
        ...


class ReviewRepository(Protocol):
    """Port for storing and reading product reviews."""

    def save(self, review: ProductReview) -> ProductReview:
        """Persist and return a review."""
        ...

    def list_for_product(self, product_identifier: str) -> list[ProductReview]:
        """Return reviews for a product identifier."""
        ...


class ScoreRepository(Protocol):
    """Port for storing product scores."""

    def save(
        self,
        product_identifier: str,
        score: ProductScore,
        inputs: ProductScoreInput,
    ) -> ProductScore:
        """Persist and return a product score."""
        ...
