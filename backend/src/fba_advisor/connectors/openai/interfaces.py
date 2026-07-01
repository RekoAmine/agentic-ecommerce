"""Protocol interfaces for the OpenAI connector."""

from typing import Protocol

from fba_advisor.connectors.openai.models import OpenAICompletion, OpenAIResponse


class OpenAIConnector(Protocol):
    """Contract implemented by OpenAI API clients."""

    @property
    def provider_name(self) -> str:
        """Return the stable provider identifier."""
        ...

    def fetch(self, value: str) -> OpenAIResponse:
        """Fetch provider data without applying business decisions."""
        ...

    def complete(self, instructions: str, value: str) -> OpenAICompletion:
        """Generate a model response from supplied instructions and input."""
        ...
