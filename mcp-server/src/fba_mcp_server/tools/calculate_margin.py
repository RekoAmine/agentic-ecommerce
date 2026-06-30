"""MCP tool for FBA margin calculation."""

import logging
from decimal import Decimal

from fba_mcp_server.schemas.requests import CalculateMarginRequest
from fba_mcp_server.schemas.responses import ToolResponse
from fba_mcp_server.tools.dependencies import get_product_research_service

logger = logging.getLogger(__name__)


def calculate_margin(
    sale_price: Decimal,
    landed_cost: Decimal,
    amazon_fees: Decimal,
    fulfillment_cost: Decimal,
) -> dict[str, object]:
    """Calculate FBA margin from validated monetary inputs."""
    request = CalculateMarginRequest(
        sale_price=sale_price,
        landed_cost=landed_cost,
        amazon_fees=amazon_fees,
        fulfillment_cost=fulfillment_cost,
    )
    logger.info("Calculating margin")
    data = get_product_research_service().calculate_margin(
        request.sale_price,
        request.landed_cost,
        request.amazon_fees,
        request.fulfillment_cost,
    )
    return ToolResponse(data=data).model_dump(mode="json")
