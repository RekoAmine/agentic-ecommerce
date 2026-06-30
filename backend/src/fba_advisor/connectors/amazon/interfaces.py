"""Protocol interfaces for the Amazon connector."""

from typing import Protocol

from fba_advisor.connectors.amazon.models import AmazonSearchResponse


class AmazonConnector(Protocol):
    """Contract implemented by Amazon API clients."""

    @property
    def provider_name(self) -> str:
        """Return the stable provider identifier."""
        ...

    def search_products(self, query: str) -> AmazonSearchResponse:
        """Search Amazon products without applying business decisions."""
        ...
