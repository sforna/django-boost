"""
Remote skill management — download skills from GitHub repositories.

Equivalent to Laravel Boost's Skills/Remote module.
"""

import os
import subprocess
import tempfile
from dataclasses import dataclass


@dataclass
class RemoteSkill:
    """A skill downloaded from a remote GitHub repository."""

    name: str
    repository: str
    path: str  # Local path after download
    description: str = ""

    def display_name(self) -> str:
        return f"{self.repository}/{self.name}"


class GitHubRepository:
    """Represents a GitHub repository used as a skill source."""

    def __init__(self, owner: str, repo: str, branch: str = "main"):
        self.owner = owner
        self.repo = repo
        self.branch = branch

    @property
    def clone_url(self) -> str:
        return f"https://github.com/{self.owner}/{self.repo}.git"

    @classmethod
    def from_input(cls, input_str: str) -> "GitHubRepository":
        """Parse a 'owner/repo' or URL string."""
        # Strip protocols and .git suffix
        cleaned = input_str.replace("https://github.com/", "").replace(".git", "")
        if ":" in cleaned:
            cleaned = cleaned.split(":")[-1]

        parts = cleaned.split("/")
        if len(parts) >= 2:
            return cls(parts[0], parts[1])
        return cls(parts[0], "")


class GitHubSkillProvider:
    """Downloads and discovers skills from a GitHub repository."""

    def __init__(self, repository: GitHubRepository):
        self._repository = repository

    def discover_skills(self) -> dict[str, RemoteSkill]:
        """Discover skills in the repository by cloning and scanning."""
        skills: dict[str, RemoteSkill] = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", "--branch", self._repository.branch,
                     self._repository.clone_url, tmpdir],
                    capture_output=True,
                    timeout=30,
                    check=True,
                )
            except Exception:
                return skills

            # Scan for SKILL.md files
            for root, dirs, files in os.walk(tmpdir):
                if "SKILL.md" in files:
                    rel = os.path.relpath(root, tmpdir)
                    skill_name = rel.replace(os.sep, "/").split("/")[-1] or os.path.basename(root)
                    description = ""
                    try:
                        with open(os.path.join(root, "SKILL.md")) as f:
                            first = f.readline().strip()
                            if first.startswith("# "):
                                description = first[2:]
                    except Exception:
                        pass
                    skills[skill_name] = RemoteSkill(
                        name=skill_name,
                        repository=f"{self._repository.owner}/{self._repository.repo}",
                        path=root,
                        description=description,
                    )

        return skills

    def download_skill(self, skill: RemoteSkill, target_dir: str) -> bool:
        """Clone the repository and extract a specific skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", "--branch", self._repository.branch,
                     self._repository.clone_url, tmpdir],
                    capture_output=True,
                    timeout=30,
                    check=True,
                )
            except Exception:
                return False

            # Copy the skill to target
            skill_path = os.path.join(tmpdir, skill.name)
            if os.path.isdir(skill_path):
                import shutil
                os.makedirs(target_dir, exist_ok=True)
                shutil.copytree(skill_path, target_dir, dirs_exist_ok=True)
                return True

        return False
