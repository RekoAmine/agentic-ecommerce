"""Application-specific exceptions for the MCP server."""


class McpServerError(Exception):
    """Base exception raised by MCP server application code."""


class ToolExecutionError(McpServerError):
    """Raised when a tool cannot complete successfully."""
