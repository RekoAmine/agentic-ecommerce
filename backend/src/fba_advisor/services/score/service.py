"""Product opportunity scoring business service."""

from dataclasses import dataclass

from fba_advisor.domain.models import ProductScore, ProductScoreInput


@dataclass(frozen=True, slots=True)
class ScoreWeights:
    """Weights for product opportunity scoring criteria."""

    demand: float = 0.30
    competition: float = 0.20
    margin: float = 0.30
    supplier: float = 0.15
    sentiment: float = 0.05


class ScoreService:
    """Score product opportunities from normalized business inputs."""

    def __init__(self, weights: ScoreWeights | None = None) -> None:
        """Inject scoring policy to keep the service configurable and testable."""
        self._weights = weights or ScoreWeights()

    def calculate(self, inputs: ProductScoreInput) -> ProductScore:
        """Return a normalized score between 0 and 100."""
        demand = self._normalize(inputs.demand_score)
        competition = 1 - self._normalize(inputs.competition_score)
        margin = self._normalize(inputs.margin_rate)
        supplier = self._normalize(inputs.supplier_reliability)
        sentiment = self._normalize(inputs.review_sentiment)
        weights = self._weights
        total_weight = (
            weights.demand
            + weights.competition
            + weights.margin
            + weights.supplier
            + weights.sentiment
        )
        if total_weight <= 0:
            msg = "score weights must have a positive sum."
            raise ValueError(msg)
        weighted = (
            demand * weights.demand
            + competition * weights.competition
            + margin * weights.margin
            + supplier * weights.supplier
            + sentiment * weights.sentiment
        ) / total_weight
        value = round(weighted * 100, 2)
        return ProductScore(value=value, rationale=self._rationale(value))

    def _normalize(self, value: float) -> float:
        return min(max(value, 0.0), 1.0)

    def _rationale(self, value: float) -> str:
        if value >= 75:
            return "Strong opportunity"
        if value >= 50:
            return "Moderate opportunity"
        return "Weak opportunity"
