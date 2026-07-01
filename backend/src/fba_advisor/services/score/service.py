"""Configurable product opportunity scoring business service."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path

from fba_advisor.domain.models import (
    ProductScore,
    ProductScoreInput,
    ProductScoringInput,
    ScoringSubScores,
)
from fba_advisor.ports.repositories import ScoreRepository


@dataclass(frozen=True, slots=True)
class ScoreWeights:
    """Weights for product opportunity scoring criteria."""

    concurrence: float = 0.20
    marge: float = 0.25
    brandabilite: float = 0.15
    differenciation: float = 0.15
    tendance: float = 0.15
    saisonnalite: float = 0.10

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> ScoreWeights:
        """Build weights from a mapping while keeping defaults for missing values."""
        defaults = cls()
        aliases = {
            "competition": "concurrence",
            "margin": "marge",
            "brandability": "brandabilite",
            "differentiation": "differenciation",
            "trend": "tendance",
            "seasonality": "saisonnalite",
        }
        normalized: dict[str, float] = {}
        for key, value in values.items():
            attr = aliases.get(str(key), str(key))
            if not hasattr(defaults, attr):
                continue
            normalized[attr] = _number(value)
        return cls(
            concurrence=normalized.get("concurrence", defaults.concurrence),
            marge=normalized.get("marge", defaults.marge),
            brandabilite=normalized.get("brandabilite", defaults.brandabilite),
            differenciation=normalized.get("differenciation", defaults.differenciation),
            tendance=normalized.get("tendance", defaults.tendance),
            saisonnalite=normalized.get("saisonnalite", defaults.saisonnalite),
        )

    def total(self) -> float:
        """Return the sum of all criterion weights."""
        return (
            self.concurrence
            + self.marge
            + self.brandabilite
            + self.differenciation
            + self.tendance
            + self.saisonnalite
        )


@dataclass(frozen=True, slots=True)
class ScoreConfig:
    """Externalized scoring configuration."""

    weights: ScoreWeights = field(default_factory=ScoreWeights)
    target_margin_rate: float = 0.30
    max_competing_offers: int = 50
    max_review_count: int = 1_000
    max_sales_rank: int = 100_000
    trend_growth_reference: float = 0.30
    seasonality_volatility_reference: float = 0.50

    @classmethod
    def from_yaml(cls, path: str | Path) -> ScoreConfig:
        """Load scoring configuration from a small YAML file."""
        data = _load_simple_yaml(Path(path))
        if not isinstance(data, dict):
            msg = "score configuration YAML must contain a mapping at the root."
            raise ValueError(msg)
        weights_data = data.get("weights", {})
        if not isinstance(weights_data, Mapping):
            msg = "score configuration 'weights' must be a mapping."
            raise ValueError(msg)
        defaults = cls()
        return cls(
            weights=ScoreWeights.from_mapping(weights_data),
            target_margin_rate=_number(data.get("target_margin_rate"), defaults.target_margin_rate),
            max_competing_offers=int(
                _number(data.get("max_competing_offers"), defaults.max_competing_offers)
            ),
            max_review_count=int(_number(data.get("max_review_count"), defaults.max_review_count)),
            max_sales_rank=int(_number(data.get("max_sales_rank"), defaults.max_sales_rank)),
            trend_growth_reference=_number(
                data.get("trend_growth_reference"), defaults.trend_growth_reference
            ),
            seasonality_volatility_reference=_number(
                data.get("seasonality_volatility_reference"),
                defaults.seasonality_volatility_reference,
            ),
        )


class ScoreService:
    """Score product opportunities from normalized and enriched business inputs."""

    def __init__(
        self,
        weights: ScoreWeights | None = None,
        repository: ScoreRepository | None = None,
        config: ScoreConfig | None = None,
        config_path: str | Path | None = None,
    ) -> None:
        """Inject scoring policy and persistence as interfaces."""
        if config_path is not None:
            config = ScoreConfig.from_yaml(config_path)
        if weights is not None:
            base = config or ScoreConfig()
            config = ScoreConfig(
                weights=weights,
                **{k: v for k, v in asdict(base).items() if k != "weights"},
            )
        self._config = config or ScoreConfig()
        self._repository = repository

    def calculate(
        self, inputs: ProductScoreInput, product_identifier: str | None = None
    ) -> ProductScore:
        """Return a legacy normalized score between 0 and 100."""
        demand = self._normalize(inputs.demand_score)
        competition = 1 - self._normalize(inputs.competition_score)
        margin = self._normalize(inputs.margin_rate)
        supplier = self._normalize(inputs.supplier_reliability)
        sentiment = self._normalize(inputs.review_sentiment)
        legacy_weights = {
            "demand": 0.30,
            "competition": 0.20,
            "margin": 0.30,
            "supplier": 0.15,
            "sentiment": 0.05,
        }
        weighted = (
            demand * legacy_weights["demand"]
            + competition * legacy_weights["competition"]
            + margin * legacy_weights["margin"]
            + supplier * legacy_weights["supplier"]
            + sentiment * legacy_weights["sentiment"]
        ) / sum(legacy_weights.values())
        value = round(weighted * 100, 2)
        score = ProductScore(value=value, rationale=self._rationale(value))
        if self._repository is not None and product_identifier is not None:
            return self._repository.save(product_identifier, score, inputs)
        return score

    def score(self, inputs: ProductScoringInput) -> ProductScore:
        """Return global score, sub-scores, and a detailed explanation."""
        sub_scores = self._sub_scores(inputs)
        weights = self._config.weights
        total_weight = weights.total()
        if total_weight <= 0:
            msg = "score weights must have a positive sum."
            raise ValueError(msg)
        weighted = (
            sum(
                getattr(sub_scores, field_name) * getattr(weights, field_name)
                for field_name in sub_scores.__dataclass_fields__
            )
            / total_weight
        )
        value = round(weighted, 2)
        return ProductScore(
            value=value,
            rationale=self._rationale(value),
            sub_scores=sub_scores,
            explanation=self._explanation(inputs, sub_scores, weights, value),
        )

    def _sub_scores(self, inputs: ProductScoringInput) -> ScoringSubScores:
        product = inputs.product
        keepa = inputs.keepa_history
        ai = inputs.ai_analysis
        review_count = _number(product.attributes.get("review_count"), keepa.get("review_count"))
        offers = _number(product.attributes.get("offer_count"), keepa.get("offer_count"))
        competition_pressure = max(
            review_count / self._config.max_review_count,
            offers / self._config.max_competing_offers,
            _number(keepa.get("competition_score")),
        )
        margin_rate = _number(keepa.get("margin_rate"), ai.get("margin_rate"))
        if margin_rate == 0 and product.price:
            cost = _number(product.attributes.get("landed_cost"), ai.get("landed_cost"))
            if cost > 0:
                margin_rate = max((product.price - cost) / product.price, 0)
        rank = _number(product.sales_rank, keepa.get("sales_rank"))
        rank_score = 1 - min(rank / self._config.max_sales_rank, 1) if rank > 0 else 0.5
        demand = _number(keepa.get("demand_score"), rank_score)
        growth = _number(keepa.get("sales_growth_rate"), keepa.get("price_growth_rate"))
        trend = max(demand, min(max(growth, 0) / self._config.trend_growth_reference, 1))
        volatility = _number(keepa.get("seasonality_index"), keepa.get("monthly_sales_cv"))
        seasonality = 1 - min(volatility / self._config.seasonality_volatility_reference, 1)
        if volatility == 0:
            seasonality = _number(ai.get("seasonality_score"), 0.5)
        brandability = _number(ai.get("brandability_score"), ai.get("brandabilite"), 0.5)
        differentiation = _number(ai.get("differentiation_score"), ai.get("differenciation"), 0.5)
        return ScoringSubScores(
            concurrence=round((1 - self._normalize(competition_pressure)) * 100, 2),
            marge=round(self._normalize(margin_rate / self._config.target_margin_rate) * 100, 2),
            brandabilite=round(self._normalize(brandability) * 100, 2),
            differenciation=round(self._normalize(differentiation) * 100, 2),
            tendance=round(self._normalize(trend) * 100, 2),
            saisonnalite=round(self._normalize(seasonality) * 100, 2),
        )

    def _normalize(self, value: float) -> float:
        return min(max(value, 0.0), 1.0)

    def _rationale(self, value: float) -> str:
        if value >= 75:
            return "Strong opportunity"
        if value >= 50:
            return "Moderate opportunity"
        return "Weak opportunity"

    def _explanation(
        self,
        inputs: ProductScoringInput,
        sub_scores: ScoringSubScores,
        weights: ScoreWeights,
        value: float,
    ) -> str:
        return (
            f"Score global {value}/100 pour {inputs.product.identifier}. "
            f"Concurrence {sub_scores.concurrence}/100, marge {sub_scores.marge}/100, "
            f"brandabilité {sub_scores.brandabilite}/100, différenciation "
            f"{sub_scores.differenciation}/100, tendance {sub_scores.tendance}/100, "
            f"saisonnalité {sub_scores.saisonnalite}/100. Pondérations: {asdict(weights)}."
        )


def _number(*values: object) -> float:
    for value in values:
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, int | float | str):
            return float(value)
    return 0.0


def _load_simple_yaml(path: Path) -> dict[str, object]:
    """Parse the limited YAML subset used by the scoring configuration."""
    result: dict[str, object] = {}
    current_mapping: dict[str, object] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" "):
            key, _, raw_value = line.partition(":")
            key = key.strip()
            raw_value = raw_value.strip()
            if raw_value:
                result[key] = _parse_yaml_scalar(raw_value)
                current_mapping = None
            else:
                current_mapping = {}
                result[key] = current_mapping
            continue
        if current_mapping is None:
            msg = f"unsupported nested YAML line: {raw_line}"
            raise ValueError(msg)
        key, _, raw_value = line.strip().partition(":")
        current_mapping[key.strip()] = _parse_yaml_scalar(raw_value.strip())
    return result


def _parse_yaml_scalar(value: str) -> object:
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value.strip("\"'")
