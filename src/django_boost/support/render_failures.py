"""
Render failures tracker — records paths that failed to render.

Equivalent to Laravel Boost's RenderFailures.
"""


class RenderFailures:
    """Tracks template rendering failures during guideline/skill composition.

    When a Blade/Jinja2 template fails to render, the path and package
    are recorded so they can be reported to the user at the end of
    installation/update.
    """

    def __init__(self):
        self._paths: list[str] = []
        self._packages: set[str] = set()

    def record(self, path: str, package: str = "") -> None:
        """Record a rendering failure."""
        self._paths.append(path)
        if package:
            self._packages.add(package)

    def paths(self) -> list[str]:
        """Get all failed paths."""
        return list(self._paths)

    def packages(self) -> list[str]:
        """Get all packages with failures."""
        return sorted(self._packages)

    def is_empty(self) -> bool:
        """Check if there are no failures."""
        return len(self._paths) == 0
