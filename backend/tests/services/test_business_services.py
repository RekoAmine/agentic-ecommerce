from pathlib import Path

from fba_advisor.domain.models import (
    MarginInput,
    Product,
    ProductReview,
    ProductScoreInput,
    ReviewDecision,
    Supplier,
)
from fba_advisor.services.margin import MarginService
from fba_advisor.services.product import ProductResearchService
from fba_advisor.services.review import ReviewService
from fba_advisor.services.score import ScoreService
from fba_advisor.services.supplier import SupplierResearchService


class _Catalog:
    def search(self, query: str) -> list[Product]:
        assert query == "coffee press"
        return [Product(identifier="B001", title="Coffee Press", source="test", price=24.99)]


class _Analytics:
    def enrich(self, product: Product) -> Product:
        return Product(
            identifier=product.identifier,
            title=product.title,
            source=product.source,
            price=product.price,
            currency=product.currency,
            sales_rank=123,
            attributes=product.attributes,
        )


class _Directory:
    def find(self, query: str) -> list[Supplier]:
        assert query == "coffee press"
        return [
            Supplier(identifier="S1", name="Low reliability", source="test", reliability_score=0.4),
            Supplier(
                identifier="S2", name="High reliability", source="test", reliability_score=0.9
            ),
        ]


class _ReviewRepository:
    def __init__(self) -> None:
        self.reviews: list[ProductReview] = []

    def save(self, review: ProductReview) -> ProductReview:
        self.reviews.append(review)
        return review

    def list_for_product(self, product_identifier: str) -> list[ProductReview]:
        return [
            review for review in self.reviews if review.product_identifier == product_identifier
        ]


def test_product_service_uses_injected_catalog_and_analytics() -> None:
    service = ProductResearchService(_Catalog(), _Analytics())

    products = service.search(" coffee press ")

    assert products == [
        Product(identifier="B001", title="Coffee Press", source="test", price=24.99, sales_rank=123)
    ]


def test_supplier_service_uses_injected_directory_and_ranks_results() -> None:
    service = SupplierResearchService(_Directory())

    suppliers = service.find(" coffee press ")

    assert [supplier.identifier for supplier in suppliers] == ["S2", "S1"]


def test_margin_service_calculates_profitability() -> None:
    estimate = MarginService().estimate(
        MarginInput(
            selling_price=40,
            product_cost=12,
            fulfillment_fee=5,
            referral_fee_rate=0.15,
            shipping_cost=3,
            fixed_costs=2,
        )
    )

    assert estimate.referral_fee == 6
    assert estimate.total_cost == 28
    assert estimate.profit == 12
    assert estimate.margin_rate == 0.3


def test_score_service_returns_normalized_opportunity_score() -> None:
    score = ScoreService().calculate(
        ProductScoreInput(
            demand_score=0.9,
            competition_score=0.2,
            margin_rate=0.3,
            supplier_reliability=0.8,
            review_sentiment=0.7,
        )
    )

    assert score.value == 67.5
    assert score.rationale == "Moderate opportunity"


def test_review_service_uses_injected_repository() -> None:
    repository = _ReviewRepository()
    service = ReviewService(repository)

    review = service.submit(" B001 ", ReviewDecision.APPROVED, " alice ", " Looks good ")

    assert review.product_identifier == "B001"
    assert review.reviewer == "alice"
    assert review.notes == "Looks good"
    assert service.list_for_product("B001") == [review]


def test_product_tool_use_cases_orchestrate_backend_services() -> None:
    from decimal import Decimal

    from fba_advisor.application.product_tools import ProductToolUseCases

    use_cases = ProductToolUseCases(
        products=ProductResearchService(_Catalog(), _Analytics()),
        margins=MarginService(),
        scores=ScoreService(),
    )

    products = use_cases.search_products(" coffee press ", 1)
    margin = use_cases.calculate_margin(
        Decimal("30.00"), Decimal("9.00"), Decimal("4.50"), Decimal("5.50")
    )
    score = use_cases.score_product("B0TEST0001", 800, 100, Decimal("30.00"))

    assert products[0].identifier == "B001"
    assert margin["net_profit"] == Decimal("11.00")
    assert score["recommendation"] == "investigate"


def test_openai_service_loads_versioned_prompts_and_routes_tasks(tmp_path: Path) -> None:
    from fba_advisor.connectors.openai.models import OpenAICompletion, OpenAIResponse
    from fba_advisor.services.openai import OpenAIService, PromptRepository

    prompt_names = [
        "competition_analysis",
        "summary",
        "review_analysis",
        "brandability",
        "differentiation",
        "ai_scoring",
    ]
    for prompt_name in prompt_names:
        (tmp_path / f"{prompt_name}.v1.md").write_text(f"prompt:{prompt_name}", encoding="utf-8")

    class _Connector:
        provider_name = "openai"

        def __init__(self) -> None:
            self.calls: list[tuple[str, str]] = []

        def fetch(self, value: str) -> OpenAIResponse:
            raise AssertionError(
                "OpenAIService must not use embedding fetch for intelligence tasks."
            )

        def complete(self, instructions: str, value: str) -> OpenAICompletion:
            self.calls.append((instructions, value))
            return OpenAICompletion(text=instructions, model="test")

    connector = _Connector()
    service = OpenAIService(connector, PromptRepository(tmp_path))

    assert service.analyse_concurrence(" data ").text == "prompt:competition_analysis"
    assert service.resume(" data ").text == "prompt:summary"
    assert service.analyse_avis(" data ").text == "prompt:review_analysis"
    assert service.brandabilite(" data ").text == "prompt:brandability"
    assert service.differenciation(" data ").text == "prompt:differentiation"
    assert service.scoring_ia(" data ").text == "prompt:ai_scoring"
    assert connector.calls == [(f"prompt:{prompt_name}", "data") for prompt_name in prompt_names]


def test_score_service_scores_product_keepa_and_ai_inputs_with_yaml_config(tmp_path: Path) -> None:
    from fba_advisor.domain.models import ProductScoringInput
    from fba_advisor.services.score import ScoreConfig

    config_path = tmp_path / "score.yaml"
    config_path.write_text(
        """
weights:
  concurrence: 0.10
  marge: 0.40
  brandabilite: 0.20
  differenciation: 0.10
  tendance: 0.10
  saisonnalite: 0.10
target_margin_rate: 0.30
max_competing_offers: 40
max_review_count: 1000
max_sales_rank: 100000
trend_growth_reference: 0.20
seasonality_volatility_reference: 0.50
""".strip(),
        encoding="utf-8",
    )
    product = Product(
        identifier="B0YAML",
        title="Premium organizer",
        source="amazon",
        price=30,
        sales_rank=20_000,
        attributes={"review_count": 100, "offer_count": 4},
    )

    score = ScoreService(config=ScoreConfig.from_yaml(config_path)).score(
        ProductScoringInput(
            product=product,
            keepa_history={
                "margin_rate": 0.24,
                "sales_growth_rate": 0.10,
                "monthly_sales_cv": 0.10,
            },
            ai_analysis={"brandability_score": 0.9, "differentiation_score": 0.7},
        )
    )

    assert score.value == 82.0
    assert score.rationale == "Strong opportunity"
    assert score.sub_scores is not None
    assert score.sub_scores.concurrence == 90
    assert score.sub_scores.marge == 80
    assert "Pondérations" in score.explanation
