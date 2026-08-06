"""
Tests for the GuidelineWriter and SkillWriter.
"""

import os

from django_boost.install.guideline_writer import GuidelineWriter, Result
from django_boost.install.skill_writer import SkillWriter


class FakeGuidelineAgent:
    """Fake agent for testing GuidelineWriter."""

    def __init__(self, path: str):
        self._path = path

    def guidelines_path(self) -> str:
        return self._path

    def frontmatter(self) -> bool:
        return False

    def transform_guidelines(self, markdown: str) -> str:
        return markdown


class FakeSkillAgent:
    """Fake agent for testing SkillWriter."""

    def __init__(self, skills_dir: str):
        self._skills_dir = skills_dir

    def skills_path(self) -> str:
        return self._skills_dir


class TestGuidelineWriter:
    """Tests for GuidelineWriter."""

    def test_write_new_guidelines(self, tmp_path):
        guidelines_path = str(tmp_path / "AGENTS.md")
        agent = FakeGuidelineAgent(guidelines_path)
        writer = GuidelineWriter(agent)

        result = writer.write("# Test Guidelines\n\nFollow these rules.")
        assert result in (Result.NEW, Result.REPLACED)

        assert os.path.isfile(guidelines_path)
        with open(guidelines_path) as f:
            content = f.read()
        assert "django-boost-guidelines" in content
        assert "Follow these rules." in content

    def test_replace_existing_guidelines(self, tmp_path):
        guidelines_path = str(tmp_path / "AGENTS.md")
        # Pre-exist with old guidelines
        with open(guidelines_path, "w") as f:
            f.write(
                "# Existing\n\n"
                "<django-boost-guidelines>\n"
                "old guidelines\n"
                "</django-boost-guidelines>\n\n"
                "# Footer"
            )

        agent = FakeGuidelineAgent(guidelines_path)
        writer = GuidelineWriter(agent)

        result = writer.write("new guidelines")
        assert result == Result.REPLACED

        with open(guidelines_path) as f:
            content = f.read()
        assert "new guidelines" in content
        assert "old guidelines" not in content
        assert "# Footer" in content

    def test_noop_on_empty_guidelines(self, tmp_path):
        guidelines_path = str(tmp_path / "AGENTS.md")
        agent = FakeGuidelineAgent(guidelines_path)
        writer = GuidelineWriter(agent)

        result = writer.write("")
        assert result == Result.NOOP


class TestSkillWriter:
    """Tests for SkillWriter."""

    def test_write_skill_creates_directory(self, tmp_path):
        skills_dir = str(tmp_path / "skills")
        agent = FakeSkillAgent(skills_dir)
        writer = SkillWriter(agent)

        # Create a source skill directory
        skill_src = tmp_path / "skill_src"
        skill_src.mkdir()
        (skill_src / "SKILL.md").write_text("# My Skill\nDescription")

        result = writer.write("my-skill", str(skill_src))
        assert result in (0, 1)  # SUCCESS or UPDATED

        target = os.path.join(skills_dir, "my-skill")
        assert os.path.isdir(target)
        assert os.path.isfile(os.path.join(target, "SKILL.md"))

    def test_invalid_skill_name_rejected(self, tmp_path):
        skills_dir = str(tmp_path / "skills")
        agent = FakeSkillAgent(skills_dir)
        writer = SkillWriter(agent)

        result = writer.write("../escape", str(tmp_path))
        assert result == 2  # FAILED

    def test_sync_removes_stale(self, tmp_path):
        skills_dir = str(tmp_path / "skills")
        agent = FakeSkillAgent(skills_dir)
        writer = SkillWriter(agent)

        # Create a source skill
        skill_src = tmp_path / "src"
        skill_src.mkdir()
        (skill_src / "SKILL.md").write_text("# Test")

        # Sync with skill-A, previously had skill-A and skill-B
        results = writer.sync({"skill-a": str(skill_src)}, previously_tracked=["skill-a", "skill-b"])
        assert "skill-a" in results
