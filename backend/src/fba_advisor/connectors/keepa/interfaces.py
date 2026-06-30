"""Protocol interfaces for the Keepa connector."""

from typing import Protocol

from fba_advisor.connectors.keepa.models import KeepaResponse


class KeepaConnector(Protocol):
    """Contract implemented by Keepa API clients."""

    @property
    def provider_name(self) -> str:
        """Return the stable provider identifier."""
        ...

    def fetch(self, value: str) -> KeepaResponse:
        """Fetch provider data without applying business decisions."""
        ...
