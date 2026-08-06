"""
SkillWriter — syncs agent skill directories.

Equivalent to Laravel Boost's SkillWriter.
"""

import os
import shutil
from enum import IntEnum
from typing import Any


class Result(IntEnum):
    """Write result status."""

    SUCCESS = 0
    UPDATED = 1
    FAILED = 2


class SkillWriter:
    """Manages agent skill directories.

    Copies skill directories from .ai/skills/ to the agent's skills path.
    """

    def __init__(self, agent: Any):
        """Initialize with an agent that supports skills.

        Args:
            agent: An object with a skills_path() method.
        """
        self._agent = agent

    def write(self, skill_name: str, skill_path: str) -> Result:
        """Write a single skill to the agent's skills directory.

        Returns SUCCESS, UPDATED, or FAILED.
        """
        if not self._is_valid_name(skill_name):
            return Result.FAILED

        target = os.path.join(self._agent.skills_path(), skill_name)
        existed = os.path.isdir(target) or os.path.islink(target)

        try:
            if os.path.isdir(target) or os.path.islink(target):
                shutil.rmtree(target)

            shutil.copytree(skill_path, target, symlinks=True)
        except OSError:
            # Fallback: copy file by file
            try:
                if os.path.isdir(target):
                    shutil.rmtree(target)
                shutil.copytree(skill_path, target, symlinks=False)
            except Exception:
                return Result.FAILED

        return Result.UPDATED if existed else Result.SUCCESS

    def write_all(self, skills: dict[str, str]) -> dict[str, Result]:
        """Write all skills. Returns {name: Result}."""
        results = {}
        for name, path in skills.items():
            results[name] = self.write(name, path)
        return results

    def sync(
        self,
        skills: dict[str, str],
        previously_tracked: list[str] | None = None,
    ) -> dict[str, Result]:
        """Write skills and remove stale ones.

        Args:
            skills: {name: path} for current skills.
            previously_tracked: list of skill names that were previously installed.
        """
        results = self.write_all(skills)

        if previously_tracked:
            new_names = set(skills.keys())
            stale = [n for n in previously_tracked if n not in new_names]
            for name in stale:
                self.remove(name)

        return results

    def remove(self, skill_name: str) -> bool:
        """Remove a skill directory from the agent."""
        if not self._is_valid_name(skill_name):
            return False

        target = os.path.join(self._agent.skills_path(), skill_name)
        try:
            if os.path.islink(target):
                os.unlink(target)
            elif os.path.isdir(target):
                shutil.rmtree(target)
            return True
        except OSError:
            return False

    def _is_valid_name(self, name: str) -> bool:
        """Validate skill name (no path traversal)."""
        if not name or not name.strip():
            return False
        if ".." in name or "/" in name or "\\" in name:
            return False
        return True
