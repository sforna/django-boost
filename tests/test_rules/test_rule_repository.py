"""
Tests for the rule repository.
"""

import os

from django_boost.rules.rule_frontmatter import parse_frontmatter, render_frontmatter
from django_boost.rules.rule_repository import RuleRepository


class TestRuleFrontmatter:
    """Tests for YAML frontmatter parsing."""

    def test_parse_with_frontmatter(self):
        content = "---\npaths:\n  - app/models/*.py\n---\n\n# Heading\nContent"
        result = parse_frontmatter(content)
        assert result["paths"] == ["app/models/*.py"]
        assert "# Heading" in result["body"]

    def test_parse_without_frontmatter(self):
        content = "# Just a heading\nSome content"
        result = parse_frontmatter(content)
        assert result["paths"] == []
        assert content in result["body"]

    def test_render_frontmatter(self):
        result = render_frontmatter(["app/views/**", "api/**"])
        assert "paths:" in result
        assert "app/views/**" in result
        assert result.startswith("---")
        assert result.endswith("---\n\n")


class TestRuleRepository:
    """Tests for RuleRepository."""

    def test_write_rule_creates_file(self, tmp_path):
        repo = RuleRepository(str(tmp_path / ".ai" / "rules"))
        path = repo.write("app/models/*.py", "Model Naming", "Use PascalCase.")

        assert os.path.isfile(path)
        with open(path) as f:
            content = f.read()
        assert "Model Naming" in content
        assert "Use PascalCase." in content
        assert "paths:" in content

    def test_write_index(self, tmp_path):
        repo = RuleRepository(str(tmp_path / ".ai" / "rules"))
        repo.write("app/views/*.py", "View Style", "Use CBVs.")
        index_path = repo.write_index()

        assert os.path.isfile(index_path)
        with open(index_path) as f:
            content = f.read()
        assert "View Style" not in content  # index only has table, not full rules
        assert "app/views/*.py" in content

    def test_normalize_glob(self):
        import os as _os

        repo = RuleRepository()
        normalized = repo.normalize_glob(f"{_os.getcwd()}/app/models/*.py")
        assert normalized == "app/models/*.py"

    def test_empty_directory_no_rules(self, tmp_path):
        repo = RuleRepository(str(tmp_path / ".ai" / "rules"))
        # Without any rules, index should still be creatable
        index_path = repo.write_index()
        assert os.path.isfile(index_path)
