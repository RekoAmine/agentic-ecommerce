"""Framework-independent domain models for business services."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class ReviewDecision(StrEnum):
    """Possible human review outcomes for a product opportunity."""

    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_MORE_DATA = "needs_more_data"


@dataclass(frozen=True, slots=True)
class Product:
    """Product candidate normalized for business decisions."""

    identifier: str
    title: str
    source: str
    price: float | None = None
    currency: str | None = None
    sales_rank: int | None = None
    attributes: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Supplier:
    """Supplier candidate normalized for sourcing decisions."""

    identifier: str
    name: str
    source: str
    minimum_order_quantity: int | None = None
    unit_cost: float | None = None
    currency: str | None = None
    reliability_score: float | None = None
    attributes: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class MarginInput:
    """Financial inputs required to estimate product margin."""

    selling_price: float
    product_cost: float
    fulfillment_fee: float = 0.0
    referral_fee_rate: float = 0.15
    shipping_cost: float = 0.0
    fixed_costs: float = 0.0


@dataclass(frozen=True, slots=True)
class MarginEstimate:
    """Estimated profit and margin for a product opportunity."""

    revenue: float
    total_cost: float
    profit: float
    margin_rate: float
    referral_fee: float


@dataclass(frozen=True, slots=True)
class ProductScoreInput:
    """Inputs used to score a product opportunity."""

    demand_score: float
    competition_score: float
    margin_rate: float
    supplier_reliability: float
    review_sentiment: float = 0.5


@dataclass(frozen=True, slots=True)
class ProductScore:
    """Computed score with a concise rationale."""

    value: float
    rationale: str


@dataclass(frozen=True, slots=True)
class ProductReview:
    """Human review record for a product opportunity."""

    product_identifier: str
    decision: ReviewDecision
    reviewer: str
    notes: str = ""
    reviewed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
