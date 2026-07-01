"""Review persistence ports used by review services."""

from typing import Protocol

from fba_advisor.domain.models import ProductReview


class ReviewRepository(Protocol):
    """Port for storing and reading product reviews."""

    def save(self, review: ProductReview) -> ProductReview:
        """Persist and return a review."""
        ...

    def list_for_product(self, product_identifier: str) -> list[ProductReview]:
        """Return reviews for a product identifier."""
        ...
