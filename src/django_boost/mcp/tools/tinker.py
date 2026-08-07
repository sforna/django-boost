"""
Tinker tool — execute Python/Django code in the application context.

Disabled by default for safety (BOOST_TINKER_TOOL_ENABLED=False).
"""

import io
import sys
import traceback

from django_boost.mcp.server import mcp


@mcp.tool(
    name="tinker",
    description=(
        "Execute Python code in the Django application context. "
        "Use for debugging issues, checking if functions exist, "
        "and testing code snippets. You should not create models "
        "directly without explicit user approval. Prefer tests "
        "for functionality testing."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": True},
)
def tinker(code: str) -> str:
    """Execute Python code in the Django application context.

    Like `manage.py shell -c`, for debugging and testing.

    Args:
        code: Python code to execute.
    """
    from django.conf import settings

    if not getattr(settings, "BOOST_TINKER_TOOL_ENABLED", False):
        raise ValueError(
            "The tinker tool is not enabled. Set BOOST_TINKER_TOOL_ENABLED=True in settings.py."
        )

    code = code.strip()
    if not code:
        raise ValueError("Please provide code to execute.")

    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()

    try:
        compiled = compile(code, "<tinker>", "exec")
        namespace: dict = {"__builtins__": __builtins__}
        exec(compiled, namespace)

        output = captured.getvalue().strip()
        return output if output else "Code executed (no output)."

    except Exception:
        traceback.print_exc(file=captured)
        raise ValueError(captured.getvalue().strip()) from None

    finally:
        sys.stdout = old_stdout
