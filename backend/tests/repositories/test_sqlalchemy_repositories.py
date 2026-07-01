from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from fba_advisor.database.base import Base
from fba_advisor.domain.models import Product, ProductScoreInput, ReviewDecision, Supplier
from fba_advisor.models import Product as ProductEntity
from fba_advisor.models import Review, Score
from fba_advisor.models import Supplier as SupplierEntity
from fba_advisor.repositories import (
    SqlAlchemyProductRepository,
    SqlAlchemyReviewRepository,
    SqlAlchemyScoreRepository,
    SqlAlchemySupplierRepository,
)
from fba_advisor.services.product import ProductResearchService
from fba_advisor.services.review import ReviewService
from fba_advisor.services.score import ScoreService
from fba_advisor.services.supplier import SupplierResearchService


class _Catalog:
    def search(self, query: str) -> list[Product]:
        return [Product(identifier="B001", title=query.title(), source="test", price=19.99)]


class _Directory:
    def find(self, query: str) -> list[Supplier]:
        return [
            Supplier(identifier="S001", name=query.title(), source="test", reliability_score=0.8)
        ]


def _session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def test_product_and_supplier_services_persist_through_repository_ports() -> None:
    factory = _session_factory()
    with factory() as session:
        products = ProductResearchService(
            _Catalog(), repository=SqlAlchemyProductRepository(session)
        ).search("coffee press")
        suppliers = SupplierResearchService(
            _Directory(), repository=SqlAlchemySupplierRepository(session)
        ).find("coffee factory")
        session.commit()

        assert products[0].identifier == "B001"
        assert suppliers[0].identifier == "S001"
        assert session.scalar(select(ProductEntity).where(ProductEntity.identifier == "B001"))
        assert session.scalar(select(SupplierEntity).where(SupplierEntity.identifier == "S001"))


def test_review_service_persists_and_lists_reviews_through_repository_port() -> None:
    factory = _session_factory()
    with factory() as session:
        service = ReviewService(SqlAlchemyReviewRepository(session))

        review = service.submit("B001", ReviewDecision.APPROVED, "alice", "valid")
        session.commit()

        assert review.decision == ReviewDecision.APPROVED
        assert session.scalar(select(Review).where(Review.product_identifier == "B001"))
        persisted = service.list_for_product("B001")
        assert len(persisted) == 1
        assert persisted[0].product_identifier == review.product_identifier
        assert persisted[0].decision == review.decision
        assert persisted[0].reviewer == review.reviewer
        assert persisted[0].notes == review.notes


def test_score_service_can_persist_without_sqlalchemy_dependency() -> None:
    factory = _session_factory()
    inputs = ProductScoreInput(
        demand_score=0.9,
        competition_score=0.2,
        margin_rate=0.3,
        supplier_reliability=0.8,
        review_sentiment=0.7,
    )
    with factory() as session:
        score = ScoreService(repository=SqlAlchemyScoreRepository(session)).calculate(
            inputs, product_identifier="B001"
        )
        session.commit()

        row = session.scalar(select(Score).where(Score.product_identifier == "B001"))
        assert row is not None
        assert float(row.value) == score.value
        assert row.inputs["demand_score"] == inputs.demand_score
