"""MCP server entrypoint and tool registration."""

import logging
from collections.abc import Callable
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from fba_mcp_server.config import McpServerSettings, get_settings
from fba_mcp_server.tools import analyse_product, calculate_margin, score_product, search_products
from fba_mcp_server.utils.logging import configure_logging

logger = logging.getLogger(__name__)
ToolCallable = Callable[..., dict[str, object]]


def _safe_tool(tool: ToolCallable) -> ToolCallable:
    """Wrap tool functions with consistent logging and error handling."""

    def wrapped(*args: Any, **kwargs: Any) -> dict[str, object]:
        try:
            return tool(*args, **kwargs)
        except ValidationError as exc:
            logger.warning("Tool validation failed", exc_info=exc)
            return {"error": "validation_error", "details": exc.errors()}
        except Exception as exc:  # noqa: BLE001 - MCP tools must return controlled errors.
            logger.exception("Tool execution failed")
            return {"error": "tool_execution_error", "details": str(exc)}

    wrapped.__name__ = tool.__name__
    wrapped.__doc__ = tool.__doc__
    return wrapped


def create_server(settings: McpServerSettings | None = None) -> FastMCP:
    """Create and configure the Agentic Ecommerce MCP server."""
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)
    server = FastMCP(resolved_settings.server_name)
    server.tool()(_safe_tool(search_products))
    server.tool()(_safe_tool(analyse_product))
    server.tool()(_safe_tool(calculate_margin))
    server.tool()(_safe_tool(score_product))
    logger.info("MCP server configured", extra={"server_name": resolved_settings.server_name})
    return server


mcp = create_server()


def main() -> None:
    """Run the MCP server using the SDK default transport."""
    mcp.run()


if __name__ == "__main__":
    main()
