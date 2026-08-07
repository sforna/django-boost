"""
boost_list_skill — List all available skills.

Usage: python manage.py boost_list_skill
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "List all available Django Boost skills"

    def handle(self, **options):
        self.stdout.write(self.style.SUCCESS("Available Skills"))
        self.stdout.write("=" * 40)

        from django_boost.install.skill_composer import SkillComposer

        composer = SkillComposer()
        skills = composer.skills()

        if not skills:
            self.stdout.write("  No skills found.")
            return

        for name, skill in sorted(skills.items()):
            tag = " (custom)" if skill.custom else ""
            self.stdout.write(f"  {skill.display_name()}{tag}")
            if skill.description:
                self.stdout.write(f"    {skill.description}")

        self.stdout.write(f"\n  Total: {len(skills)} skills")
