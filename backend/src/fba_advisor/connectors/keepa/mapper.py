"""Mapping utilities for Keepa API responses."""

from fba_advisor.connectors.keepa.exceptions import KeepaParsingError
from fba_advisor.connectors.keepa.models import KeepaProduct, KeepaResponse


def map_response(payload: dict[str, object]) -> KeepaResponse:
    """Transform a raw Keepa payload into typed connector models."""
    products = payload.get("products", [])
    if not isinstance(products, list):
        raise KeepaParsingError("Keepa payload must contain a 'products' list.")
    items: list[KeepaProduct] = []
    for product in products:
        if not isinstance(product, dict):
            raise KeepaParsingError("Keepa product must be an object.")
        asin = product.get("asin")
        if not isinstance(asin, str):
            raise KeepaParsingError("Keepa product requires string 'asin'.")
        rank = product.get("salesRank")
        if rank is not None and not isinstance(rank, int):
            raise KeepaParsingError("Keepa 'salesRank' must be an integer or null.")
        title = product.get("title")
        if title is not None and not isinstance(title, str):
            raise KeepaParsingError("Keepa 'title' must be a string or null.")
        items.append(KeepaProduct(asin=asin, title=title, sales_rank=rank, raw=product))
    return KeepaResponse(items=items)
