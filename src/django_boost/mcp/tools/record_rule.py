"""
RecordRule tool — record a durable project rule for future agents.
"""

import os

from django_boost.mcp.server import mcp


@mcp.tool(
    name="record-rule",
    description=(
        "Record a durable project rule so the next agent or teammate inherits "
        "it instead of working it out again. Use it for a settled decision "
        "(why the project does something a certain way), a non-obvious trap, "
        "or a standing constraint that must always be followed. Pass a glob "
        "for the files it applies to and Boost files it into a shared, "
        "committed markdown note grouped by area. Keep it to a few lines; "
        "only record what you would want to read in three months."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True},
)
def record_rule(
    glob: str,
    title: str,
    note: str,
) -> str:
    """Record a durable project rule.

    Args:
        glob: Glob for the files this rule applies to (e.g. 'app/controllers/**').
        title: A short, specific heading (e.g. 'Extend BaseController for tenant scoping').
        note: A few lines stating the rule plainly. No essays.
    """
    from django.conf import settings

    if not getattr(settings, "BOOST_RULES_ENABLED", True):
        raise ValueError("Project rules are disabled (BOOST_RULES_ENABLED=False).")

    glob_val = glob.strip()
    title = title.strip()
    note = note.strip()

    missing = []
    if not glob_val:
        missing.append("glob")
    if not title:
        missing.append("title")
    if not note:
        missing.append("note")
    if missing:
        raise ValueError(
            f"A rule needs a non-empty glob, title, and note. Missing or empty: {', '.join(missing)}."
        )

    try:
        rules_dir = os.path.join(os.getcwd(), ".ai", "rules")
        os.makedirs(rules_dir, exist_ok=True)

        file_path = _resolve_target_file(rules_dir, glob_val)

        entry = f"\n## {title}\n{note}\n"

        if os.path.exists(file_path):
            with open(file_path, "a") as f:
                f.write(entry)
        else:
            heading = os.path.splitext(os.path.basename(file_path))[0]
            heading = heading.replace("-", " ").title()
            frontmatter = f"---\npaths:\n  - {glob_val}\n---\n"
            with open(file_path, "w") as f:
                f.write(f"{frontmatter}\n# {heading}{entry}")

        rel_path = os.path.relpath(file_path, os.getcwd())
        return f"Recorded rule in {rel_path}: {title}."

    except Exception as e:
        raise ValueError(f"Failed to write rule: {e}") from e


def _resolve_target_file(rules_dir: str, glob_val: str) -> str:
    """Determine the target file for a given glob."""
    segments = []
    for part in glob_val.replace("\\", "/").split("/"):
        part = part.strip()
        if part and not any(c in part for c in "*.[]"):
            segments.append(part)

    filename = "-".join(s.lower().replace("_", "-") for s in segments) if segments else "general"
    return os.path.join(rules_dir, f"{filename}.md")
