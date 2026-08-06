"""
Shared log-reading utilities for MCP tools.

Equivalent to Laravel Boost's ReadsLogs trait.
"""

import glob
import re
from typing import List, Optional


def resolve_log_file_path(log_name: str = "django") -> str:
    """Resolve the path to a log file.

    Checks Django's LOGGING settings first, then falls back to common locations.
    """
    import os

    # Try to get from Django settings
    try:
        from django.conf import settings

        handlers = settings.LOGGING.get("handlers", {})
        loggers = settings.LOGGING.get("loggers", {})

        # Check the specific logger
        logger_config = loggers.get(log_name, {})
        handler_names = logger_config.get("handlers", [])

        for hname in handler_names:
            handler = handlers.get(hname, {})
            if handler.get("class", "").endswith("FileHandler") or "filename" in handler:
                path = handler.get("filename", "")
                if path and os.path.exists(path):
                    return path
    except Exception:
        pass

    # Fallback paths
    base = os.getcwd()
    candidates = [
        os.path.join(base, "logs", f"{log_name}.log"),
        os.path.join(base, "storage", "logs", f"{log_name}.log"),
        os.path.join(base, "var", "log", f"{log_name}.log"),
        os.path.join("/var/log", f"{log_name}.log"),
    ]

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    return candidates[0]


def read_last_log_entries(log_file: str, num_entries: int) -> list[str]:
    """Read the last N log entries from a file, handling multi-line PSR-3-like logs.

    A new log entry starts with a line matching a standard log pattern:
    [YYYY-MM-DD HH:MM:SS] or similar.
    """
    lines = _read_lines_reverse(log_file, num_entries * 20)
    lines.reverse()

    entries: list[str] = []
    current_entry: list[str] = []

    log_pattern = re.compile(
        r'^\[?\d{4}[-/]\d{2}[-/]\d{2}[ T]\d{2}:\d{2}:\d{2}'
    )

    for line in lines:
        if log_pattern.match(line) and current_entry:
            entries.append("".join(current_entry))
            current_entry = [line.rstrip("\n")]
        else:
            current_entry.append(line.rstrip("\n"))

    if current_entry:
        entries.append("".join(current_entry))

    # Return last N entries
    return entries[-num_entries:]


def read_last_error_entry(log_file: str) -> Optional[str]:
    """Read the last ERROR entry from a log file."""
    lines = _read_lines_reverse(log_file, 200)
    lines.reverse()

    current_entry: list[str] = []
    log_pattern = re.compile(
        r'^\[?\d{4}[-/]\d{2}[-/]\d{2}[ T]\d{2}:\d{2}:\d{2}'
    )
    error_pattern = re.compile(r'(ERROR|CRITICAL|FATAL|Exception|Traceback)', re.IGNORECASE)

    found_error = False
    for line in reversed(lines):
        if log_pattern.match(line):
            if found_error:
                entries = ["".join(current_entry)]
                return entries[0][:500]
            current_entry = [line.rstrip("\n")]
            if error_pattern.search(line):
                found_error = True
        else:
            current_entry.append(line.rstrip("\n"))

    return None


def _read_lines_reverse(file_path: str, max_lines: int) -> list[str]:
    """Read up to max_lines from the end of a file."""
    try:
        with open(file_path, "rb") as f:
            f.seek(0, 2)  # End of file
            file_size = f.tell()
            if file_size == 0:
                return []

            buf_size = min(8192, file_size)
            lines: list[str] = []
            buffer = bytearray()
            pos = file_size

            while pos > 0 and len(lines) < max_lines:
                read_size = min(buf_size, pos)
                pos -= read_size
                f.seek(pos)
                buffer[:0] = f.read(read_size)
                # Split keeping newlines
                decoded = buffer.decode("utf-8", errors="replace")
                new_lines = decoded.split("\n")
                if pos == 0:
                    lines = new_lines + lines
                else:
                    lines = new_lines[1:] + lines
                buffer = bytearray(new_lines[0].encode("utf-8", errors="replace"))

            return lines[-max_lines:]

    except (FileNotFoundError, OSError):
        return []
