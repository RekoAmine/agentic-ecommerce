"""Standard-library tracing adapter for local and test environments."""

import logging
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from time import perf_counter
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LoggingSpan:
    """In-memory span that emits lifecycle events through Python logging."""

    trace_id: str
    span_id: str
    name: str
    attributes: dict[str, object] = field(default_factory=dict)

    def set_attribute(self, key: str, value: object) -> None:
        """Attach an attribute to the span."""
        self.attributes[key] = value


class LoggingTracer:
    """Tracer implementation backed by structured log records."""

    @contextmanager
    def start_span(
        self, name: str, attributes: Mapping[str, object] | None = None
    ) -> Iterator[LoggingSpan]:
        """Log span start, finish, duration, and errors."""
        span = LoggingSpan(
            trace_id=uuid4().hex,
            span_id=uuid4().hex[:16],
            name=name,
            attributes=dict(attributes or {}),
        )
        started_at = perf_counter()
        logger.info("trace.span.start", extra={"trace": _span_payload(span)})
        try:
            yield span
        except Exception:
            span.set_attribute("error", True)
            logger.exception("trace.span.error", extra={"trace": _span_payload(span)})
            raise
        finally:
            span.set_attribute("duration_ms", round((perf_counter() - started_at) * 1000, 2))
            logger.info("trace.span.finish", extra={"trace": _span_payload(span)})


def _span_payload(span: LoggingSpan) -> dict[str, object]:
    """Return a logging-safe representation of a span."""
    return {
        "trace_id": span.trace_id,
        "span_id": span.span_id,
        "name": span.name,
        "attributes": span.attributes,
    }
