"""Logging / observability setup.

Kept separate so a concrete project can bolt on tracing (e.g. Langfuse,
OpenTelemetry) in one place without touching request handlers.
"""

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging to emit lines to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
