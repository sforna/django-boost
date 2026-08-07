"""
LastError tool — returns the last error from the application log.
"""

import logging

from django_boost.mcp.server import mcp

from .logs import read_last_error_entry, resolve_log_file_path

# Module-level state for the in-process log listener.
_listener_registered = False
_last_error_cache: dict | None = None


class _BoostLogHandler(logging.Handler):
    """Log handler that caches the last ERROR record."""

    def emit(self, record: logging.LogRecord) -> None:
        global _last_error_cache
        if record.levelno >= logging.ERROR:
            _last_error_cache = {
                "timestamp": self.format(record) if self.formatter else str(record.created),
                "level": record.levelname,
                "message": record.getMessage(),
            }


def _ensure_listener() -> None:
    """Register the Boost log handler once per process."""
    global _listener_registered
    if not _listener_registered:
        handler = _BoostLogHandler()
        handler.setLevel(logging.ERROR)
        logging.getLogger().addHandler(handler)
        _listener_registered = True


@mcp.tool(
    name="last-error",
    description=(
        "Get details of the last error/exception created in this application "
        "on the backend. Use browser-logs tool for browser errors."
    ),
    annotations={"readOnlyHint": True},
)
def last_error() -> str:
    """Return the last backend error from logs."""
    _ensure_listener()

    global _last_error_cache

    if _last_error_cache is not None:
        cached = (
            f"[{_last_error_cache['timestamp']}] "
            f"{_last_error_cache['level']}: "
            f"{_last_error_cache['message']}"
        )
        return cached[:500]

    log_file = resolve_log_file_path()
    entry = read_last_error_entry(log_file)

    if entry:
        return entry[:500]

    raise ValueError("Unable to find an ERROR entry in the log file.")
