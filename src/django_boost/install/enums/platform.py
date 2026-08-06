"""
Platform detection for agent installation.

Equivalent to Laravel Boost's Platform enum.
"""

import platform
from enum import Enum


class Platform(Enum):
    """Operating system platform for agent detection."""

    DARWIN = "darwin"
    LINUX = "linux"
    WINDOWS = "windows"
    UNKNOWN = "unknown"

    @classmethod
    def current(cls) -> "Platform":
        """Detect the current platform."""
        system = platform.system().lower()
        mapping = {
            "darwin": cls.DARWIN,
            "linux": cls.LINUX,
            "windows": cls.WINDOWS,
        }
        return mapping.get(system, cls.UNKNOWN)
