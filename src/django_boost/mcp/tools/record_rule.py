"""
RecordRule tool — record a durable project rule for future agents.

Equivalent to Laravel Boost's RecordRule tool.
"""

import os
from typing import Any

from django.conf import settings as django_settings

from .base import BoostTool


class RecordRule(BoostTool):
    """Record a durable project rule so the next agent or teammate inherits it.

    Use for settled decisions, non-obvious traps, or standing constraints.
    Pass a glob for the files it applies to - Boost files it into a shared,
    committed markdown note grouped by area.
    """

    name = "record-rule"
    description = (
        "Record a durable project rule so the next agent or teammate inherits "
        "it instead of working it out again. Use it for a settled decision "
        "(why the project does something a certain way), a non-obvious trap, "
        "or a standing constraint that must always be followed. Pass a glob "
        "for the files it applies to and Boost files it into a shared, "
        "committed markdown note grouped by area. Keep it to a few lines; "
        "only record what you would want to read in three months."
    )
    is_read_only = False
    enabled_by_default = True

    def should_register(self) -> bool:
        return getattr(django_settings, "BOOST_RULES_ENABLED", True)

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "glob": {
                    "type": "string",
                    "description": (
                        "Glob for the files this rule applies to, "
                        "e.g. 'app/controllers/**' or 'models/*.py'."
                    ),
                },
                "title": {
                    "type": "string",
                    "description": (
                        "A short, specific heading, e.g. 'Extend BaseController for tenant scoping'."
                    ),
                },
                "note": {
                    "type": "string",
                    "description": "A few lines stating the rule plainly. No essays.",
                },
            },
            "required": ["glob", "title", "note"],
        }

    async def call(self, arguments: dict) -> list[dict]:
        glob_val = arguments.get("glob", "").strip()
        title = arguments.get("title", "").strip()
        note = arguments.get("note", "").strip()

        missing = []
        if not glob_val:
            missing.append("glob")
        if not title:
            missing.append("title")
        if not note:
            missing.append("note")
        if missing:
            return self._error(
                f"A rule needs a non-empty glob, title, and note. "
                f"Missing or empty: {', '.join(missing)}."
            )

        try:
            rules_dir = self._rules_dir()
            os.makedirs(rules_dir, exist_ok=True)

            # Determine target file from glob
            file_path = self._resolve_target_file(rules_dir, glob_val)

            # Write the rule entry
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
            return self._ok(f"Recorded rule in {rel_path}: {title}.")

        except Exception as e:
            return self._error(f"Failed to write rule: {e}")

    def _rules_dir(self) -> str:
        """Get the .ai/rules directory path."""
        return os.path.join(os.getcwd(), ".ai", "rules")

    def _resolve_target_file(self, rules_dir: str, glob_val: str) -> str:
        """Determine the target file for a given glob.

        Groups rules by directory area, using meaningful path segments.
        """
        # Extract meaningful directory segments from the glob
        segments = []
        for part in glob_val.replace("\\", "/").split("/"):
            part = part.strip()
            if part and not any(c in part for c in "*.[]"):
                segments.append(part)

        if not segments:
            filename = "general"
        else:
            filename = "-".join(s.lower().replace("_", "-") for s in segments)

        return os.path.join(rules_dir, f"{filename}.md")
