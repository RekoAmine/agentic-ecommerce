"""Typed models for Bright Data connector payloads."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class BrightDataTarget(StrEnum):
    """Supported Bright Data target families."""

    AMAZON = "amazon"
    ALIBABA = "alibaba"
    GOOGLE = "google"


class BrightDataCredentials(BaseModel):
    """Credentials required to call Bright Data APIs."""

    api_token: str
    zone: str | None = None


class BrightDataRecord(BaseModel):
    """Generic parsed Bright Data record."""

    model_config = ConfigDict(frozen=True)

    target: BrightDataTarget
    identifier: str | None = None
    title: str | None = None
    url: str | None = None
    raw: dict[str, object] = Field(default_factory=dict)


class BrightDataResponse(BaseModel):
    """Parsed Bright Data response."""

    target: BrightDataTarget
    records: list[BrightDataRecord]
