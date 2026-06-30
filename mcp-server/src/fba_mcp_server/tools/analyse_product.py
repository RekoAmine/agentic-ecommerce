"""MCP tool for product analysis."""

import logging

from fba_mcp_server.schemas.requests import AnalyseProductRequest
from fba_mcp_server.schemas.responses import ToolResponse
from fba_mcp_server.tools.dependencies import get_product_research_service

logger = logging.getLogger(__name__)


def analyse_product(asin: str, marketplace: str = "amazon_us") -> dict[str, object]:
    """Analyse a product with simulated signals."""
    request = AnalyseProductRequest(asin=asin, marketplace=marketplace)
    logger.info(
        "Analysing product",
        extra={"asin": request.asin, "marketplace": request.marketplace},
    )
    data = get_product_research_service().analyse_product(request)
    return ToolResponse(data=data).model_dump(mode="json")
