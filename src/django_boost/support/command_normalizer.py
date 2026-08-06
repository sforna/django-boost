"""
Command normalizer — splits shell commands into executable + args.

Equivalent to Laravel Boost's CommandNormalizer.
"""

import re
import shlex


def normalize_command(command: str, args: list[str] | None = None) -> dict:
    """Normalize a command string into {command, args}.

    Handles quoted strings and absolute paths with spaces.

    Args:
        command: The shell command string (e.g., "php artisan boost:mcp")
        args: Additional arguments to append.

    Returns:
        {"command": "php", "args": ["artisan", "boost:mcp"]}
    """
    args = args or []

    # If it's an absolute path, keep it intact
    if command.startswith("/") or re.match(r"^[A-Za-z]:\\", command):
        return {"command": command, "args": args}

    try:
        parts = shlex.split(command)
    except ValueError:
        # Fallback: split by spaces, respecting quotes
        parts = re.findall(r'"[^"]*"|\'[^\']*\'|\S+', command)
        parts = [p.strip("\"'") for p in parts]

    if len(parts) > 1:
        return {"command": parts[0], "args": parts[1:] + args}

    return {"command": command, "args": args}
