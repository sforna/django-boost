"""
ReadLogEntries tool — reads the last N entries from the application log.

Equivalent to Laravel Boost's ReadLogEntries tool.
"""

from typing import Any

from .base import BoostTool
from .logs import read_last_log_entries, resolve_log_file_path


class ReadLogEntries(BoostTool):
    """Read the last N log entries from the application log.

    Correctly handles multi-line logs and JSON-formatted logs.
    Only works for file-based log handlers.
    """

    name = "read-log-entries"
    description = (
        "Read the last N log entries from the application log, correctly "
        "handling multi-line logs and JSON-formatted logs. "
        "Only works for log files."
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

        log_file = resolve_log_file_path()

        try:
            with open(log_file):
                pass
        except FileNotFoundError:
            return self._error(f"Log file not found: {log_file}")

        entries = read_last_log_entries(log_file, num_entries)

        if not entries:
            return self._ok("No log entries yet.")

        return self._ok("\n\n".join(entries))
