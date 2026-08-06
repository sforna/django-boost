"""
BrowserLogs tool — reads the last N entries from the browser log.

Equivalent to Laravel Boost's BrowserLogs tool.
"""

from typing import Any

from .base import BoostTool
from .logs import read_last_log_entries, resolve_log_file_path


class BrowserLogs(BoostTool):
    """Read the last N log entries from the BROWSER log.

    Very helpful for debugging frontend/JavaScript issues.
    """

    name = "browser-logs"
    description = (
        "Read the last N log entries from the BROWSER log. "
        "Very helpful for debugging the frontend and JavaScript."
    )
    is_read_only = True

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entries": {
                    "type": "integer",
                    "description": "Number of log entries to return.",
                },
            },
            "required": ["entries"],
        }

    async def call(self, arguments: dict) -> list[dict]:
        num_entries = arguments.get("entries", 10)

        if num_entries <= 0:
            return self._error('The "entries" argument must be greater than 0.')

        log_file = resolve_log_file_path("browser")

        try:
            with open(log_file):
                pass
        except FileNotFoundError:
            return self._ok("No log file found, probably means no logs yet.")

        entries = read_last_log_entries(log_file, num_entries)

        if not entries:
            return self._ok("No log entries yet.")

        return self._ok("\n\n".join(entries))
