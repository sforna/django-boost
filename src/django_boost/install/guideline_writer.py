"""
GuidelineWriter — writes AI guidelines to agent config files.

Equivalent to Laravel Boost's GuidelineWriter.
"""

import os
import time
from enum import IntEnum
from typing import Any, Protocol

import random


class Result(IntEnum):
    """Write result status."""
    NEW = 0
    REPLACED = 1
    FAILED = 2
    NOOP = 3


class GuidelineWriter:
    """Writes AI guidelines into agent-specific config files.

    Manages the <django-boost-guidelines>...</django-boost-guidelines> block
    within MDX/Markdown-based agent configuration files.
    """

    GUIDELINES_TAG = "django-boost-guidelines"

    def __init__(self, agent: Any):
        """Initialize with an agent that supports guidelines.

        Args:
            agent: An object with guidelines_path(), frontmatter(),
                   and transform_guidelines() methods.
        """
        self._agent = agent

    def write(self, guidelines: str) -> Result:
        """Write guidelines to the agent's config file.

        Returns one of: NEW, REPLACED, FAILED, NOOP.
        """
        if not guidelines:
            return Result.NOOP

        guidelines = self._agent.transform_guidelines(guidelines)
        file_path = self._agent.guidelines_path()
        directory = os.path.dirname(file_path)

        if directory and not os.path.isdir(directory):
            try:
                os.makedirs(directory, 0o755, exist_ok=True)
            except OSError:
                return Result.FAILED

        try:
            if os.path.isfile(file_path):
                handle = open(file_path, "r+")
            else:
                handle = open(file_path, "a+")
                # a+ positions at end, seek back to start
                handle.seek(0)
        except OSError:
            return Result.FAILED

        try:
            self._acquire_lock(handle, file_path)
            content = handle.read()

            tag_open = f"<{self.GUIDELINES_TAG}>"
            tag_close = f"</{self.GUIDELINES_TAG}>"
            replacement = f"{tag_open}\n{guidelines}\n\n{tag_close}"
            replaced = False

            if tag_open in content:
                # Replace existing guidelines block
                import re
                pattern = re.compile(
                    f"<{self.GUIDELINES_TAG}>.*?</{self.GUIDELINES_TAG}>",
                    re.DOTALL,
                )
                new_content = pattern.sub(
                    lambda m: replacement, content, count=1
                )
                replaced = True
            else:
                # Append to end
                frontmatter = ""
                if self._agent.frontmatter() and "---" not in content:
                    frontmatter = "---\nalwaysApply: true\n---\n"

                existing = content.rstrip()
                separator = "" if not existing else "\n\n===\n\n"
                new_content = f"{frontmatter}{existing}{separator}{replacement}"

            # Normalize blank lines
            import re
            new_content = re.sub(r"\n{3,}", "\n\n", new_content)

            if not new_content.endswith("\n"):
                new_content += "\n"

            handle.seek(0)
            handle.truncate(0)
            handle.write(new_content)
            handle.flush()

        finally:
            handle.close()

        return Result.REPLACED if replaced else Result.NEW

    def _acquire_lock(self, handle, file_path: str, max_retries: int = 3) -> None:
        """Acquire a flock with exponential backoff."""
        import fcntl

        delay = 0.1  # 100ms
        for attempt in range(max_retries):
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return
            except BlockingIOError:
                if attempt >= max_retries - 1:
                    return  # Best effort
                time.sleep(delay + random.uniform(0, delay * 0.1))
                delay *= 2
