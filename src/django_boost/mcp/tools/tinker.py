"""
Tinker tool — execute Python/Django code in the application context.

Equivalent to Laravel Boost's Tinker tool.
Disabled by default for safety (BOOST_TINKER_TOOL_ENABLED=False).
"""

import io
import sys
import traceback
from typing import Any

from django.conf import settings

from .base import BoostTool


class Tinker(BoostTool):
    """Execute Python code in the Django application context.

    Like `manage.py shell -c`, for debugging and testing code snippets.
    Do not create models without explicit user approval.
    Disabled by default — enable with BOOST_TINKER_TOOL_ENABLED=True.
    """

    name = "tinker"
    description = (
        "Execute Python code in the Django application context. "
        "Use for debugging issues, checking if functions exist, "
        "and testing code snippets. You should not create models "
        "directly without explicit user approval. Prefer tests "
        "for functionality testing."
    )
    is_read_only = False
    enabled_by_default = False

    def should_register(self) -> bool:
        """Check if the tool is enabled in settings."""
        return getattr(settings, "BOOST_TINKER_TOOL_ENABLED", False)

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute.",
                },
            },
            "required": ["code"],
        }

    async def call(self, arguments: dict) -> list[dict]:
        code = arguments.get("code", "").strip()

        if not code:
            return self._error("Please provide code to execute.")

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured = io.StringIO()

        try:
            # Compile and execute in a single expression/statement context
            compiled = compile(code, "<tinker>", "exec")

            # Build the namespace with useful Django imports
            namespace = {
                "__builtins__": __builtins__,
            }

            exec(compiled, namespace)

            output = captured.getvalue().strip()
            return self._ok(output if output else "Code executed (no output).")

        except Exception:
            traceback.print_exc(file=captured)
            return self._error(captured.getvalue().strip())

        finally:
            sys.stdout = old_stdout
