"""MCP tool for product opportunity scoring."""

import logging
from decimal import Decimal

from fba_mcp_server.schemas.requests import ScoreProductRequest
from fba_mcp_server.schemas.responses import ToolResponse
from fba_mcp_server.tools.dependencies import get_product_research_service

logger = logging.getLogger(__name__)


def score_product(
    asin: str,
    monthly_sales_estimate: int,
    review_count: int,
    margin_percent: Decimal,
) -> dict[str, object]:
    """Score a product opportunity with simulated decision rules."""
    request = ScoreProductRequest(
        asin=asin,
        monthly_sales_estimate=monthly_sales_estimate,
        review_count=review_count,
        margin_percent=margin_percent,
    )
    logger.info("Scoring product", extra={"asin": request.asin})
    data = get_product_research_service().score_product(request)
    return ToolResponse(data=data).model_dump(mode="json")
