"""Mapping utilities for OpenAI API responses."""

from fba_advisor.connectors.openai.exceptions import OpenAIParsingError
from fba_advisor.connectors.openai.models import OpenAICompletion, OpenAIEmbedding, OpenAIResponse


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


def map_completion(payload: dict[str, object], model: str) -> OpenAICompletion:
    """Transform a raw OpenAI Responses API payload into a typed completion."""
    text = payload.get("output_text")
    if isinstance(text, str):
        return OpenAICompletion(text=text, model=model, raw=payload)

    output = payload.get("output")
    if not isinstance(output, list):
        raise OpenAIParsingError("OpenAI completion payload must contain output text.")
    parts: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for content_item in content:
            if not isinstance(content_item, dict):
                continue
            content_text = content_item.get("text")
            if isinstance(content_text, str):
                parts.append(content_text)
    if not parts:
        raise OpenAIParsingError("OpenAI completion payload did not include text content.")
    return OpenAICompletion(text="\n".join(parts), model=model, raw=payload)
