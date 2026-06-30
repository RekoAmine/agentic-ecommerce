"""Mapping utilities for OpenAI API responses."""

from fba_advisor.connectors.openai.exceptions import OpenAIParsingError
from fba_advisor.connectors.openai.models import OpenAIEmbedding, OpenAIResponse


def map_response(payload: dict[str, object], text: str, model: str) -> OpenAIResponse:
    """Transform a raw OpenAI embeddings payload into typed connector models."""
    data = payload.get("data", [])
    if not isinstance(data, list):
        raise OpenAIParsingError("OpenAI payload must contain a 'data' list.")
    items: list[OpenAIEmbedding] = []
    for item in data:
        if not isinstance(item, dict):
            raise OpenAIParsingError("OpenAI data item must be an object.")
        vector = item.get("embedding")
        if not isinstance(vector, list) or not all(isinstance(v, int | float) for v in vector):
            raise OpenAIParsingError("OpenAI embedding must be a numeric list.")
        items.append(
            OpenAIEmbedding(text=text, vector=[float(v) for v in vector], model=model, raw=item)
        )
    return OpenAIResponse(items=items)
