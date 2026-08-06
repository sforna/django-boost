"""
Rule frontmatter parser — parses YAML frontmatter from rule markdown files.

Equivalent to Laravel Boost's RuleFrontmatter.
"""

import yaml


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from a markdown string.

    Returns {"paths": [...], "body": "..."}
    """
    if not content.startswith("---"):
        return {"paths": [], "body": content}

    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return {"paths": [], "body": content}

    try:
        fm = yaml.safe_load(parts[1])
        paths = fm.get("paths", []) if isinstance(fm, dict) else []
    except yaml.YAMLError:
        paths = []

    return {"paths": paths, "body": parts[2]}


def render_frontmatter(paths: list[str]) -> str:
    """Render YAML frontmatter with glob paths.

    Returns "---\\npaths: [...]\\n---\\n\\n"
    """
    return f"---\n{yaml.dump({'paths': list(paths)}, default_flow_style=False)}---\n\n"
