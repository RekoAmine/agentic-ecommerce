"""Agent-related ports used by application services.

The backend depends on these abstractions only. Concrete agent runtimes, MCP
clients, or model providers belong in infrastructure adapters.
"""

from typing import Protocol


class DecisionAgent(Protocol):
    """Contract implemented by an AI agent capable of handling a decision task."""

    @property
    def name(self) -> str:
        """Return the stable agent name used for orchestration and observability."""
        ...
