"""
Template rendering utilities for guidelines and skills.

Equivalent to Laravel Boost's RendersBladeGuidelines trait.
"""

import re


def render_template(content: str, context: dict | None = None) -> str:
    """Render a Jinja2 template string with the given context.

    Handles placeholder protection for code blocks and inline code.
    """
    context = context or {}

    # Protect backticks and other special tokens from Jinja2 processing
    placeholders = {
        "`": "___SINGLE_BACKTICK___",
        "{%": "___OPEN_JINJA_TAG___",
        "{{": "___OPEN_JINJA_VAR___",
        "{% end": "___CLOSE_JINJA_TAG___",
    }

    content_protected = content
    for orig, placeholder in placeholders.items():
        content_protected = content_protected.replace(orig, placeholder)

    try:
        from jinja2 import Template
        template = Template(content_protected)
        rendered = template.render(context)
    except Exception:
        return content

    # Restore placeholders
    for orig, placeholder in placeholders.items():
        rendered = rendered.replace(placeholder, orig)

    return rendered


def render_template_file(file_path: str, context: dict | None = None) -> str:
    """Render a Jinja2 template file."""
    try:
        with open(file_path, "r") as f:
            content = f.read()
    except Exception:
        return ""

    return render_template(content, context)


def format_markdown(content: str) -> str:
    """Format markdown content consistently.

    - Ensures single trailing newline
    - Collapses 3+ blank lines into 2
    """
    content = content.strip()
    # Collapse 3+ newlines
    content = re.sub(r"\n{3,}", "\n\n", content)
    if content and not content.endswith("\n"):
        content += "\n"
    return content
