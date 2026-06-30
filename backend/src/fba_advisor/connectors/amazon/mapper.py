"""Mapping utilities for Amazon API responses."""

from fba_advisor.connectors.amazon.exceptions import AmazonParsingError
from fba_advisor.connectors.amazon.models import AmazonProduct, AmazonSearchResponse


def map_search_response(payload: dict[str, object], marketplace_id: str) -> AmazonSearchResponse:
    """Transform a raw Amazon search payload into typed connector models."""
    items = payload.get("items", [])
    if not isinstance(items, list):
        msg = "Amazon search payload must contain an 'items' list."
        raise AmazonParsingError(msg)

    products: list[AmazonProduct] = []
    for item in items:
        if not isinstance(item, dict):
            msg = "Amazon search item must be an object."
            raise AmazonParsingError(msg)
        asin = item.get("asin")
        title = item.get("title")
        if not isinstance(asin, str) or not isinstance(title, str):
            msg = "Amazon search item requires string 'asin' and 'title'."
            raise AmazonParsingError(msg)
        products.append(
            AmazonProduct(
                asin=asin,
                title=title,
                marketplace_id=marketplace_id,
                price=_optional_float(item.get("price")),
                currency=_optional_str(item.get("currency")),
                raw=item,
            )
        )
    return AmazonSearchResponse(products=products)


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    msg = "Expected numeric value or null."
    raise AmazonParsingError(msg)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    msg = "Expected string value or null."
    raise AmazonParsingError(msg)
