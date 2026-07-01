"""SQLAlchemy models for persisted marketplace research data."""

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fba_advisor.database.base import Base


class TimestampMixin:
    """Common timestamp columns for persistent entities."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class Category(TimestampMixin, Base):
    """Product category tree."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)

    parent: Mapped["Category | None"] = relationship(
        remote_side="Category.id", back_populates="children"
    )
    children: Mapped[list["Category"]] = relationship(back_populates="parent")
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Supplier(TimestampMixin, Base):
    """Supplier capable of sourcing products."""

    __tablename__ = "suppliers"
    __table_args__ = (
        UniqueConstraint("source", "identifier", name="uq_suppliers_source_identifier"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    minimum_order_quantity: Mapped[int | None] = mapped_column(Integer)
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str | None] = mapped_column(String(3))
    reliability_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    attributes: Mapped[dict[str, object]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=False
    )

    products: Mapped[list["Product"]] = relationship(back_populates="supplier")
    quotes: Mapped[list["Quote"]] = relationship(back_populates="supplier")
    emails: Mapped[list["Email"]] = relationship(back_populates="supplier")


class Product(TimestampMixin, Base):
    """Product candidate normalized for FBA research."""

    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("source", "identifier", name="uq_products_source_identifier"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str | None] = mapped_column(String(3))
    sales_rank: Mapped[int | None] = mapped_column(Integer)
    attributes: Mapped[dict[str, object]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=False
    )
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"))

    category: Mapped[Category | None] = relationship(back_populates="products")
    supplier: Mapped[Supplier | None] = relationship(back_populates="products")
    reviews: Mapped[list["Review"]] = relationship(back_populates="product")
    scores: Mapped[list["Score"]] = relationship(back_populates="product")
    quotes: Mapped[list["Quote"]] = relationship(back_populates="product")
    emails: Mapped[list["Email"]] = relationship(back_populates="product")


class Review(TimestampMixin, Base):
    """Human review of a product opportunity."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    product_identifier: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    reviewer: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    product: Mapped[Product | None] = relationship(back_populates="reviews")


class Score(TimestampMixin, Base):
    """Computed product opportunity score."""

    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    product_identifier: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    inputs: Mapped[dict[str, object]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=False
    )

    product: Mapped[Product | None] = relationship(back_populates="scores")


class Quote(TimestampMixin, Base):
    """Supplier quote for a product candidate."""

    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    minimum_order_quantity: Mapped[int | None] = mapped_column(Integer)
    lead_time_days: Mapped[int | None] = mapped_column(Integer)
    terms: Mapped[str] = mapped_column(Text, default="", nullable=False)

    product: Mapped[Product | None] = relationship(back_populates="quotes")
    supplier: Mapped[Supplier | None] = relationship(back_populates="quotes")


class Email(TimestampMixin, Base):
    """Email exchanged with a supplier about a product."""

    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"))
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    product: Mapped[Product | None] = relationship(back_populates="emails")
    supplier: Mapped[Supplier | None] = relationship(back_populates="emails")
