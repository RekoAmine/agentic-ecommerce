"""Protocol interfaces for the Bright Data connector."""

from typing import Protocol

from fba_advisor.connectors.brightdata.models import BrightDataResponse, BrightDataTarget


class BrightDataConnector(Protocol):
    """Contract implemented by Bright Data clients."""

    @property
    def provider_name(self) -> str:
        """Return the stable provider identifier."""
        ...

    def collect(self, target: BrightDataTarget, query: str) -> BrightDataResponse:
        """Collect raw target data without applying business decisions."""
        ...
