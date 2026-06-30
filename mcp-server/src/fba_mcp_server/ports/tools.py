"""Tool abstractions exposed by the MCP server."""

from typing import Protocol


class McpTool(Protocol):
    """Contract for a single MCP tool adapter."""

    @property
    def tool_name(self) -> str:
        """Return the stable tool name exposed to agent clients."""
        ...
