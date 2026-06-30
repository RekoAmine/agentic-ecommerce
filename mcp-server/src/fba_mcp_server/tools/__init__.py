"""Tool adapters exposed by the MCP server."""

from fba_mcp_server.tools.analyse_product import analyse_product
from fba_mcp_server.tools.calculate_margin import calculate_margin
from fba_mcp_server.tools.score_product import score_product
from fba_mcp_server.tools.search_products import search_products

__all__ = ["analyse_product", "calculate_margin", "score_product", "search_products"]
