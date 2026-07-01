"""Product review business service using repository injection."""

from fba_advisor.domain.models import ProductReview, ReviewDecision
from fba_advisor.ports.reviews import ReviewRepository


class ReviewService:
    """Submit and read product reviews without knowing persistence adapters."""

    def __init__(self, repository: ReviewRepository) -> None:
        """Inject review repository as an interface."""
        self._repository = repository

    def submit(
        self,
        product_identifier: str,
        decision: ReviewDecision,
        reviewer: str,
        notes: str = "",
    ) -> ProductReview:
        """Validate and persist a product review."""
        if not product_identifier.strip():
            msg = "product_identifier is required."
            raise ValueError(msg)
        if not reviewer.strip():
            msg = "reviewer is required."
            raise ValueError(msg)
        review = ProductReview(
            product_identifier=product_identifier.strip(),
            decision=decision,
            reviewer=reviewer.strip(),
            notes=notes.strip(),
        )
        return self._repository.save(review)

    def list_for_product(self, product_identifier: str) -> list[ProductReview]:
        """Return reviews for a product identifier."""
        if not product_identifier.strip():
            return []
        return self._repository.list_for_product(product_identifier.strip())
