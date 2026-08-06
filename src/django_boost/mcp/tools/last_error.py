"""
LastError tool — returns the last error from the application log.

Equivalent to Laravel Boost's LastError tool.
"""

import logging
from typing import Optional

from .base import BoostTool
from .logs import read_last_error_entry, resolve_log_file_path

# Module-level state for the log listener
_listener_registered = False
_last_error_cache: Optional[dict] = None


class _BoostLogHandler(logging.Handler):
    """Log handler that caches the last ERROR record."""

    def emit(self, record):
        global _last_error_cache
        if record.levelno >= logging.ERROR:
            _last_error_cache = {
                "timestamp": self.format(record) if self.formatter else str(record.created),
                "level": record.levelname,
                "message": record.getMessage(),
            }


def _ensure_listener():
    """Register the Boost log handler once per process."""
    global _listener_registered
    if not _listener_registered:
        handler = _BoostLogHandler()
        handler.setLevel(logging.ERROR)
        logger = logging.getLogger()  # Root logger
        logger.addHandler(handler)
        _listener_registered = True


class LastError(BoostTool):
    """Get details of the last error/exception created in this application.

    Use browser-logs tool for browser/frontend errors.
    """

    name = "last-error"
    description = (
        "Get details of the last error/exception created in this application "
        "on the backend. Use browser-logs tool for browser errors."
    )
    is_read_only = True

    async def call(self, arguments: dict) -> list[dict]:
        _ensure_listener()

        global _last_error_cache

        # First try the in-process cache
        if _last_error_cache is not None:
            cached_entry = (
                f"[{_last_error_cache['timestamp']}] "
                f"{_last_error_cache['level']}: "
                f"{_last_error_cache['message']}"
            )
            return self._ok(cached_entry[:500])

        # Fall back to reading the log file
        log_file = resolve_log_file_path()
        entry = read_last_error_entry(log_file)

        if entry:
            return self._ok(entry[:500])

        return self._error("Unable to find an ERROR entry in the log file.")
