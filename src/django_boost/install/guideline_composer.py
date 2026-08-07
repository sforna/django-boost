"""
GuidelineComposer — discovers and composes AI guidelines from templates.

Equivalent to Laravel Boost's GuidelineComposer.
"""

import os
from typing import Any


class GuidelineComposer:
    """Discovers and composes AI guideline templates into a single markdown string.

    Guidelines come from:
    - Built-in templates (.ai/ directory in the package)
    - Third-party packages
    - User custom guidelines (.ai/guidelines/)
    """

    def __init__(self, guideline_config: Any | None = None):
        self._config = guideline_config

    def compose(self) -> str:
        """Compose all guidelines into a single markdown string.

        Returns the composed guidelines ready to be written to agent files.
        """
        sections = []

        # Built-in foundation guidelines
        foundation = self._render_builtin_guideline("foundation")
        if foundation:
            sections.append(foundation)

        # Django core guidelines
        django_core = self._render_builtin_guideline("django/core")
        if django_core:
            sections.append(django_core)

        # Django Boost intro
        boost_intro = self._render_builtin_guideline("django_boost/core")
        if boost_intro:
            sections.append(boost_intro)

        # Key packages with versions (auto-generated)
        packages = self._render_builtin_guideline("packages")
        if packages:
            sections.append(packages)

        # Test framework guidelines
        tests = self._render_builtin_guideline("pytest/core")
        if tests:
            sections.append(tests)

        # User custom guidelines
        custom = self._render_user_guidelines()
        if custom:
            sections.append(custom)

        return "\n\n".join(sections)

    def _render_builtin_guideline(self, name: str) -> str | None:
        """Render a built-in guideline template.

        Templates are looked up in the templates/boost/ directory.
        """

        template_dirs = []

        # Check if the package has templates
        import django_boost

        pkg_dir = os.path.dirname(django_boost.__file__)
        builtin_dir = os.path.join(pkg_dir, "templates", "boost")
        template_dirs.append(builtin_dir)

        for template_dir in template_dirs:
            # Try .html first, then .md
            for ext in (".html", ".md"):
                path = os.path.join(template_dir, f"{name}{ext}")
                if os.path.isfile(path):
                    try:
                        with open(path, "r") as f:
                            content = f.read()
                        return self._render_template(content, path)
                    except Exception:
                        return None

        return None

    def _render_user_guidelines(self) -> str | None:
        """Render user-created custom guidelines from .ai/guidelines/."""
        user_dir = os.path.join(os.getcwd(), ".ai", "guidelines")
        if not os.path.isdir(user_dir):
            return None

        parts = []
        try:
            for fname in sorted(os.listdir(user_dir)):
                if fname.endswith((".md", ".html")):
                    path = os.path.join(user_dir, fname)
                    with open(path, "r") as f:
                        content = f.read()
                    rendered = self._render_template(content, path)
                    if rendered:
                        parts.append(rendered)
        except OSError:
            return None

        return "\n\n".join(parts) if parts else None

    def _render_template(self, content: str, path: str) -> str:
        """Render a template, processing Jinja2 if it's an HTML file."""
        if path.endswith(".html"):
            try:
                from jinja2 import Template

                template = Template(content)
                context = {
                    "assist": self._get_assist(),
                    "config": self._config,
                }
                return template.render(context)
            except Exception:
                pass
        return content

    def _get_assist(self):
        """Get template assistance helper."""
        from .guideline_assist import GuidelineAssist

        assist = GuidelineAssist()
        if self._config and getattr(self._config, "has_skills", False):
            assist.set_skills_enabled(True)
        return assist
