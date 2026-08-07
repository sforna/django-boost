"""
BrowserLogs tool — reads the last N entries from the browser log.
"""

from django_boost.mcp.server import mcp

from .logs import read_last_log_entries, resolve_log_file_path


@mcp.tool(
    name="browser-logs",
    description=(
        "Read the last N log entries from the BROWSER log. "
        "Very helpful for debugging the frontend and JavaScript."
    ),
    annotations={"readOnlyHint": True},
)
def browser_logs(entries: int) -> str:
    """Read the last N entries from the browser console log.

    Args:
        entries: Number of log entries to return.
    """
    if entries <= 0:
        raise ValueError('The "entries" argument must be greater than 0.')

    log_file = resolve_log_file_path("browser")

    try:
        with open(log_file):
            pass
    except FileNotFoundError:
        return "No log file found, probably means no logs yet."

    lines = read_last_log_entries(log_file, entries)

    if not lines:
        return "No log entries yet."

    return "\n\n".join(lines)
