"""
ReadLogEntries tool — reads the last N entries from the application log.
"""

from django_boost.mcp.server import mcp
from .logs import read_last_log_entries, resolve_log_file_path


@mcp.tool(
    name="read-log-entries",
    description=(
        "Read the last N log entries from the application log, correctly "
        "handling multi-line logs and JSON-formatted logs. "
        "Only works for log files."
    ),
    annotations={"readOnlyHint": True},
)
def read_log_entries(entries: int) -> str:
    """Read the last N entries from the application log file.

    Args:
        entries: Number of log entries to return.
    """
    if entries <= 0:
        raise ValueError('The "entries" argument must be greater than 0.')

    log_file = resolve_log_file_path()

    try:
        with open(log_file):
            pass
    except FileNotFoundError:
        raise ValueError(f"Log file not found: {log_file}") from None

    lines = read_last_log_entries(log_file, entries)

    if not lines:
        return "No log entries yet."

    return "\n\n".join(lines)
