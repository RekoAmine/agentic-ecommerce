"""Tracing ports used by application services for observability."""

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Protocol


class Span(Protocol):
    """A unit of traced work."""

    def set_attribute(self, key: str, value: object) -> None:
        """Attach an attribute to the active span."""
        ...


class Tracer(Protocol):
    """Port implemented by tracing adapters."""

    @contextmanager
    def start_span(
        self, name: str, attributes: Mapping[str, object] | None = None
    ) -> Iterator[Span]:
        """Start and yield a tracing span."""
        ...
