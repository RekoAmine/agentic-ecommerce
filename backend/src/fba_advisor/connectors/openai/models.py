"""Typed models for OpenAI connector payloads."""

from pydantic import BaseModel, ConfigDict, Field


class OpenAICredentials(BaseModel):
    """Credentials required to call OpenAI APIs."""

    api_key: str
    organization: str | None = None


class OpenAIEmbedding(BaseModel):
    """Parsed OpenAI data returned by the connector."""

    model_config = ConfigDict(frozen=True)

    text: str
    vector: list[float]
    model: str
    raw: dict[str, object] = Field(default_factory=dict)


class OpenAIResponse(BaseModel):
    """Parsed OpenAI response."""

    items: list[OpenAIEmbedding]
