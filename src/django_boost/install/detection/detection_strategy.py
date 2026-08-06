"""
Detection strategies for agent discovery.

Equivalent to Laravel Boost's detection strategies.
"""

import os
import subprocess
from abc import ABC, abstractmethod

from ..enums.platform import Platform


class DetectionStrategy(ABC):
    """Abstract base for agent detection strategies."""

    @abstractmethod
    def detect(self, config: dict, platform: Platform | None = None) -> bool:
        """Check if the agent is present."""
        ...


class CommandDetectionStrategy(DetectionStrategy):
    """Detect via shell command (e.g., `which pi`)."""

    def detect(self, config: dict, platform: Platform | None = None) -> bool:
        command = config.get("command", "")
        if not command:
            return False
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False


class FileDetectionStrategy(DetectionStrategy):
    """Detect via presence of a file."""

    def detect(self, config: dict, platform: Platform | None = None) -> bool:
        files = config.get("files", [])
        base_path = config.get("basePath", os.getcwd())

        for file_path in files:
            full_path = os.path.join(base_path, file_path)
            if os.path.isfile(full_path):
                return True
        return False


class DirectoryDetectionStrategy(DetectionStrategy):
    """Detect via presence of a directory."""

    def detect(self, config: dict, platform: Platform | None = None) -> bool:
        paths = config.get("paths", [])
        base_path = config.get("basePath", os.getcwd())

        for path in paths:
            full_path = os.path.join(base_path, path)
            if os.path.isdir(full_path):
                return True
        return False


class CompositeDetectionStrategy(DetectionStrategy):
    """Combine multiple detection strategies (OR logic)."""

    def __init__(self, strategies: list[DetectionStrategy] | None = None):
        self._strategies = strategies or []

    def detect(self, config: dict, platform: Platform | None = None) -> bool:
        for strategy in self._strategies:
            if strategy.detect(config, platform):
                return True
        return False
