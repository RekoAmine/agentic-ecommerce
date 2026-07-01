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
class ScoringSubScores:
    """Detailed opportunity sub-scores on a 0-100 scale."""

    concurrence: float
    marge: float
    brandabilite: float
    differenciation: float
    tendance: float
    saisonnalite: float


@dataclass(frozen=True, slots=True)
class ProductScoringInput:
    """Rich inputs used by the configurable scoring engine."""

    product: Product
    keepa_history: dict[str, object] = field(default_factory=dict)
    ai_analysis: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProductScore:
    """Computed score with rationale, sub-scores, and explanation."""

    value: float
    rationale: str
    sub_scores: ScoringSubScores | None = None
    explanation: str = ""


@dataclass(frozen=True, slots=True)
class ProductReview:
    """Human review record for a product opportunity."""

    product_identifier: str
    decision: ReviewDecision
    reviewer: str
    notes: str = ""
    reviewed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
