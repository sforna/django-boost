"""
SkillComposer — discovers and manages agent skills.

Equivalent to Laravel Boost's SkillComposer.
"""

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class Skill:
    """Represents an agent skill with its metadata."""

    name: str
    package: str
    path: str
    description: str
    custom: bool = False

    def display_name(self) -> str:
        if self.custom:
            return f".ai/{self.name}*"
        return self.name


class SkillComposer:
    """Discovers and manages agent skills.

    Skills come from:
    - Built-in skills (shipped with django-boost)
    - User custom skills (.ai/skills/)
    - Remote skills (GitHub)
    """

    def __init__(self, guideline_config: Any | None = None):
        self._config = guideline_config

    def skills(self) -> dict[str, Skill]:
        """Get all discovered skills.

        Returns {name: Skill} mapping.
        """
        skills: dict[str, Skill] = {}

        # Core skills (built-in)
        for skill in self._get_core_skills():
            skills[skill.name] = skill

        # Built-in boost skills
        for skill in self._get_boost_skills():
            skills[skill.name] = skill

        # User custom skills
        for skill in self._get_user_skills():
            skills[skill.name] = skill

        return skills

    def _get_core_skills(self) -> list[Skill]:
        """Get core skills shipped with django-boost."""
        import django_boost

        pkg_dir = os.path.dirname(django_boost.__file__)
        skills_dir = os.path.join(pkg_dir, "templates", "boost")

        skills = []
        if os.path.isdir(skills_dir):
            for entry in sorted(os.listdir(skills_dir)):
                entry_path = os.path.join(skills_dir, entry)
                if not os.path.isdir(entry_path):
                    continue

                # Look for skill directories (contain SKILL.md)
                skill_subdir = os.path.join(entry_path, "skill")
                if os.path.isdir(skill_subdir):
                    for skill_name in sorted(os.listdir(skill_subdir)):
                        skill_path = os.path.join(skill_subdir, skill_name)
                        if os.path.isdir(skill_path):
                            skill = self._parse_skill_dir(skill_name, "django-boost", skill_path)
                            if skill:
                                skills.append(skill)

        return skills

    def _get_boost_skills(self) -> list[Skill]:
        """Get django-boost internal skills (e.g., infer-conventions)."""
        return []

    def _get_user_skills(self) -> list[Skill]:
        """Get user-created custom skills from .ai/skills/."""
        user_dir = os.path.join(os.getcwd(), ".ai", "skills")
        if not os.path.isdir(user_dir):
            return []

        skills = []
        try:
            for entry in sorted(os.listdir(user_dir)):
                entry_path = os.path.join(user_dir, entry)
                if os.path.isdir(entry_path):
                    skill = self._parse_skill_dir(entry, "user", entry_path, custom=True)
                    if skill:
                        skills.append(skill)
        except OSError:
            pass

        return skills

    def _parse_skill_dir(self, name: str, package: str, path: str, custom: bool = False) -> Skill | None:
        """Parse a skill directory and return a Skill object."""
        skill_md = os.path.join(path, "SKILL.md")
        description = ""

        if os.path.isfile(skill_md):
            try:
                with open(skill_md, "r") as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("# "):
                        description = first_line[2:]
                    else:
                        description = first_line
            except Exception:
                pass

        return Skill(
            name=name,
            package=package,
            path=path,
            description=description or name,
            custom=custom,
        )
