"""
GuidelineConfig — configuration object for guideline composition.

Equivalent to Laravel Boost's GuidelineConfig.
"""


class GuidelineConfig:
    """Configuration passed to the guideline and skill composers.

    Tracks which features are enabled, which packages/guidelines
    should be included, and project-specific settings.
    """

    def __init__(self):
        self.enforce_tests: bool = True
        self.has_api: bool = False
        self.ai_guidelines: list[str] = []
        self.uses_sail: bool = False
        self.has_skills: bool = False
        self.has_mcp: bool = False

    def has_skills_enabled(self) -> bool:
        return self.has_skills
