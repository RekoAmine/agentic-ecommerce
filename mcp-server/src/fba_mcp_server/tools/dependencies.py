"""Shared dependencies for MCP tool adapters."""

from fba_mcp_server.interfaces.product_service import ProductResearchService
from fba_mcp_server.services.product_research import SimulatedProductResearchService


def get_product_research_service() -> ProductResearchService:
    """Build the product research service dependency."""
    return SimulatedProductResearchService()
