"""Mapping utilities for Bright Data responses."""

from fba_advisor.connectors.brightdata.exceptions import BrightDataParsingError
from fba_advisor.connectors.brightdata.models import (
    BrightDataRecord,
    BrightDataResponse,
    BrightDataTarget,
)


def map_response(payload: dict[str, object], target: BrightDataTarget) -> BrightDataResponse:
    """Transform a raw Bright Data payload into generic connector records."""
    records = payload.get("records", payload.get("data", []))
    if not isinstance(records, list):
        msg = "Bright Data payload must contain a 'records' or 'data' list."
        raise BrightDataParsingError(msg)

    parsed: list[BrightDataRecord] = []
    for record in records:
        if not isinstance(record, dict):
            msg = "Bright Data record must be an object."
            raise BrightDataParsingError(msg)
        parsed.append(
            BrightDataRecord(
                target=target,
                identifier=_optional_str(record.get("id", record.get("asin"))),
                title=_optional_str(record.get("title", record.get("name"))),
                url=_optional_str(record.get("url")),
                raw=record,
            )
        )
    return BrightDataResponse(target=target, records=parsed)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    msg = "Expected string value or null."
    raise BrightDataParsingError(msg)
