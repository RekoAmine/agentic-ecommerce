"""Data-provider ports for external marketplace, catalog, and analytics sources."""

from typing import Protocol


class DataProvider(Protocol):
    """Contract for pluggable external data providers."""

    @property
    def provider_name(self) -> str:
        """Return the stable provider identifier."""
        ...
