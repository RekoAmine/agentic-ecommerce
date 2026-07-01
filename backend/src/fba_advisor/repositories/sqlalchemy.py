"""SQLAlchemy repository adapters implementing service persistence ports."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from fba_advisor.domain.models import Product as DomainProduct
from fba_advisor.domain.models import ProductReview, ProductScore, ProductScoreInput, ReviewDecision
from fba_advisor.domain.models import Supplier as DomainSupplier
from fba_advisor.models import Product, Review, Score, Supplier


class SqlAlchemyProductRepository:
    """Persist domain products with SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        """Create the repository with an active SQLAlchemy session."""
        self._session = session

    def save(self, product: DomainProduct) -> DomainProduct:
        """Upsert a product by source and identifier."""
        entity = self._session.scalar(
            select(Product).where(
                Product.source == product.source,
                Product.identifier == product.identifier,
            )
        )
        if entity is None:
            entity = Product(
                identifier=product.identifier, source=product.source, title=product.title
            )
            self._session.add(entity)
        entity.title = product.title
        entity.price = Decimal(str(product.price)) if product.price is not None else None
        entity.currency = product.currency
        entity.sales_rank = product.sales_rank
        entity.attributes = dict(product.attributes)
        self._session.flush()
        return product


class SqlAlchemySupplierRepository:
    """Persist domain suppliers with SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        """Create the repository with an active SQLAlchemy session."""
        self._session = session

    def save(self, supplier: DomainSupplier) -> DomainSupplier:
        """Upsert a supplier by source and identifier."""
        entity = self._session.scalar(
            select(Supplier).where(
                Supplier.source == supplier.source,
                Supplier.identifier == supplier.identifier,
            )
        )
        if entity is None:
            entity = Supplier(
                identifier=supplier.identifier,
                source=supplier.source,
                name=supplier.name,
            )
            self._session.add(entity)
        entity.name = supplier.name
        entity.minimum_order_quantity = supplier.minimum_order_quantity
        entity.unit_cost = (
            Decimal(str(supplier.unit_cost)) if supplier.unit_cost is not None else None
        )
        entity.currency = supplier.currency
        entity.reliability_score = (
            Decimal(str(supplier.reliability_score))
            if supplier.reliability_score is not None
            else None
        )
        entity.attributes = dict(supplier.attributes)
        self._session.flush()
        return supplier


class SqlAlchemyReviewRepository:
    """Persist and retrieve product reviews with SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        """Create the repository with an active SQLAlchemy session."""
        self._session = session

    def save(self, review: ProductReview) -> ProductReview:
        """Persist and return a product review."""
        self._session.add(
            Review(
                product_identifier=review.product_identifier,
                decision=review.decision.value,
                reviewer=review.reviewer,
                notes=review.notes,
                reviewed_at=review.reviewed_at,
            )
        )
        self._session.flush()
        return review

    def list_for_product(self, product_identifier: str) -> list[ProductReview]:
        """Return persisted reviews for a product identifier."""
        rows = self._session.scalars(
            select(Review)
            .where(Review.product_identifier == product_identifier)
            .order_by(Review.reviewed_at)
        ).all()
        return [
            ProductReview(
                product_identifier=row.product_identifier,
                decision=ReviewDecision(row.decision),
                reviewer=row.reviewer,
                notes=row.notes,
                reviewed_at=row.reviewed_at,
            )
            for row in rows
        ]


class SqlAlchemyScoreRepository:
    """Persist product scores with SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        """Create the repository with an active SQLAlchemy session."""
        self._session = session

    def save(
        self,
        product_identifier: str,
        score: ProductScore,
        inputs: ProductScoreInput,
    ) -> ProductScore:
        """Persist and return a product score."""
        self._session.add(
            Score(
                product_identifier=product_identifier,
                value=Decimal(str(score.value)),
                rationale=score.rationale,
                inputs={
                    "demand_score": inputs.demand_score,
                    "competition_score": inputs.competition_score,
                    "margin_rate": inputs.margin_rate,
                    "supplier_reliability": inputs.supplier_reliability,
                    "review_sentiment": inputs.review_sentiment,
                },
            )
        )
        self._session.flush()
        return score
