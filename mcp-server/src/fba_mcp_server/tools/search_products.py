"""MCP tool for product search."""

import logging

from fba_mcp_server.schemas.products import Marketplace
from fba_mcp_server.schemas.requests import SearchProductsRequest
from fba_mcp_server.schemas.responses import ToolResponse
from fba_mcp_server.tools.dependencies import get_product_research_service

logger = logging.getLogger(__name__)


def search_products(
    query: str, marketplace: str = "amazon_us", limit: int = 5
) -> dict[str, object]:
    """Search products with simulated catalog data."""
    request = SearchProductsRequest(query=query, marketplace=Marketplace(marketplace), limit=limit)
    logger.info(
        "Searching products",
        extra={"query": request.query, "marketplace": request.marketplace},
    )
    data = get_product_research_service().search_products(request)
    return ToolResponse(data=data).model_dump(mode="json")
