"""Supplier business service implemented through injected ports."""

from fba_advisor.domain.models import Supplier
from fba_advisor.ports.catalog import SupplierDirectory
from fba_advisor.ports.repositories import SupplierRepository


class SupplierResearchService:
    """Find and rank supplier candidates without direct connector access."""

    def __init__(
        self, directory: SupplierDirectory, repository: SupplierRepository | None = None
    ) -> None:
        """Inject supplier dependencies as interfaces."""
        self._directory = directory
        self._repository = repository

    def find(self, query: str) -> list[Supplier]:
        """Return suppliers ordered by known reliability, then known unit cost."""
        normalized_query = query.strip()
        if not normalized_query:
            return []
        suppliers = self._directory.find(normalized_query)
        if self._repository is not None:
            suppliers = [self._repository.save(supplier) for supplier in suppliers]
        return sorted(
            suppliers,
            key=lambda supplier: (
                supplier.reliability_score is None,
                -(supplier.reliability_score or 0.0),
                supplier.unit_cost is None,
                supplier.unit_cost or 0.0,
            ),
        )
