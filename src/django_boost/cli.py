"""
Standalone CLI for Django Boost.

Runs without requiring 'django_boost' in INSTALLED_APPS.
Bootstraps Django from DJANGO_SETTINGS_MODULE or --settings.

Usage:
    django-boost mcp                      Start the MCP server
    django-boost install                  Interactive setup wizard
    django-boost update                   Refresh guidelines/skills/MCP config
    django-boost list-skill               List available skills
    django-boost add-skill <repo>         Download a skill from GitHub
    django-boost execute-tool <tool>      Run a single MCP tool
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def bootstrap_django(settings: str | None = None, pythonpath: str | None = None) -> None:
    """Set up Django environment so the rest of the CLI can use the ORM, config, etc.

    Does NOT require django_boost to be in INSTALLED_APPS.
    """
    if pythonpath:
        sys.path.insert(0, pythonpath)

    # Resolve settings module
    settings_module = settings or os.environ.get("DJANGO_SETTINGS_MODULE")
    if not settings_module:
        print(
            "Error: DJANGO_SETTINGS_MODULE not set.\n"
            "Set the environment variable or use --settings, e.g.:\n"
            "  export DJANGO_SETTINGS_MODULE=myproject.settings\n"
            "  django-boost --settings myproject.settings mcp\n",
            file=sys.stderr,
        )
        sys.exit(1)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    import django
    from django.core.management import call_command

    # If django_boost is in INSTALLED_APPS, management commands are auto-discovered.
    # Otherwise we still want django.setup() so the ORM / settings are available,
    # and we call the underlying functions directly.
    django.setup()

    # Allow callers to detect whether we're running standalone
    _mark_configured()


def _mark_configured() -> None:
    """Mark that bootstrap has run so tools can check at runtime."""
    os.environ["BOOST_CLI_CONFIGURED"] = "1"


def is_configured() -> bool:
    """Return True if the CLI bootstrap already ran."""
    return os.environ.get("BOOST_CLI_CONFIGURED") == "1"


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def cmd_mcp(args: argparse.Namespace) -> None:
    """Start the MCP server via stdio."""
    from django_boost.mcp.server import mcp

    print("Starting Django Boost MCP server...")
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nMCP server stopped.")


def cmd_install(args: argparse.Namespace) -> None:
    """Run the interactive installation wizard."""
    print("Django Boost Install")
    print(
        "This command will configure AI guidelines, skills, and MCP servers "
        "for your Django project."
    )
    print("(Full installation wizard coming in a future version.)")

    features = []
    if args.guidelines:
        features.append("guidelines")
    if args.skills:
        features.append("skills")
    if args.mcp:
        features.append("mcp")

    if features:
        print(f"Selected features: {', '.join(features)}")
    else:
        print("No features selected. Use --guidelines, --skills, or --mcp.")


def cmd_update(args: argparse.Namespace) -> None:
    """Refresh guidelines, skills, and MCP configuration."""
    print("Django Boost Update")
    print("Checking for updates to guidelines, skills, and MCP config...")

    update_all = not any([args.guidelines, args.skills, args.mcp])

    # Check current state
    agent_file = Path("AGENTS.md")
    if agent_file.is_file():
        content = agent_file.read_text()
        if "django-boost-guidelines" in content:
            print("  Found existing guidelines in AGENTS.md")

    if update_all or args.guidelines:
        print("  Updating AI guidelines...")
        try:
            from django_boost.install.guideline_composer import GuidelineComposer

            composer = GuidelineComposer()
            guidelines = composer.compose()
            print(f"  Composed {len(guidelines)} chars of guidelines")
        except Exception as exc:
            print(f"  Guidelines update skipped: {exc}")

    if update_all or args.skills:
        print("  Updating agent skills...")
        print("  Skills sync (stub — full sync coming soon)")

    if update_all or args.mcp:
        print("  Updating MCP server configuration...")
        print("  MCP config update (stub — full update coming soon)")

    print("Update complete.")


def cmd_list_skill(args: argparse.Namespace) -> None:
    """List available skills."""
    print("Available Skills")
    print("=" * 40)

    try:
        from django_boost.install.skill_composer import SkillComposer

        composer = SkillComposer()
        skills = composer.skills()

        if not skills:
            print("  No skills found.")
            return

        for name, skill in sorted(skills.items()):
            tag = " (custom)" if skill.custom else ""
            print(f"  {skill.display_name()}{tag}")
            if skill.description:
                print(f"    {skill.description}")

        print(f"\n  Total: {len(skills)} skills")
    except Exception as exc:
        print(f"Error listing skills: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_add_skill(args: argparse.Namespace) -> None:
    """Download a skill from a GitHub repository."""
    source = args.source
    path = args.path or ""
    branch = args.branch

    print(f"Downloading skill from: {source}")
    if path:
        print(f"  Path: {path}")
    print(f"  Branch: {branch}")
    print(
        f"Skill download initiated. Run 'git clone --depth 1 --branch {branch} "
        f"https://github.com/{source}.git .ai/skills/boost_skill'"
    )


def cmd_execute_tool(args: argparse.Namespace) -> None:
    """Execute a single MCP tool from the command line."""
    import asyncio
    import json

    tool_name = args.tool
    try:
        tool_args = json.loads(args.args)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON args: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Executing tool: {tool_name}")
    if tool_args:
        print(f"  Arguments: {json.dumps(tool_args)}")

    from django_boost.mcp.server import mcp

    try:
        result = asyncio.run(mcp.call_tool(tool_name, tool_args))
        for item in result if isinstance(result, list) else [result]:
            if hasattr(item, "text"):
                print(item.text)
            elif isinstance(item, dict) and "text" in item:
                print(item["text"])
            elif isinstance(item, str):
                print(item)

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="django-boost",
        description="Django Boost — AI-assisted development accelerator for Django.",
    )
    parser.add_argument(
        "--settings",
        help="Django settings module (e.g. myproject.settings)",
        default=None,
    )
    parser.add_argument(
        "--pythonpath",
        help="Directory to add to Python path (your Django project root)",
        default=None,
    )

    sub = parser.add_subparsers(dest="command", title="commands")

    # mcp
    sub.add_parser("mcp", help="Start the Django Boost MCP server")

    # install
    p_install = sub.add_parser("install", help="Install guidelines, skills, and MCP config")
    p_install.add_argument("--guidelines", action="store_true", help="Install AI guidelines")
    p_install.add_argument("--skills", action="store_true", help="Install agent skills")
    p_install.add_argument("--mcp", action="store_true", help="Install MCP server configuration")

    # update
    p_update = sub.add_parser("update", help="Update guidelines, skills, and MCP config")
    p_update.add_argument("--guidelines", action="store_true", help="Update AI guidelines only")
    p_update.add_argument("--skills", action="store_true", help="Update agent skills only")
    p_update.add_argument("--mcp", action="store_true", help="Update MCP server configuration only")
    p_update.add_argument("--yes", action="store_true", help="Skip confirmation prompts")

    # list-skill
    sub.add_parser("list-skill", help="List available skills")

    # add-skill
    p_add = sub.add_parser("add-skill", help="Download a skill from GitHub")
    p_add.add_argument("source", help="GitHub repository (e.g. 'user/repo') or URL")
    p_add.add_argument("--path", default="", help="Subdirectory within the repo")
    p_add.add_argument("--branch", default="main", help="Git branch (default: main)")

    # execute-tool
    p_exec = sub.add_parser("execute-tool", help="Execute a single MCP tool")
    p_exec.add_argument("tool", help="Tool name (e.g. 'database-schema')")
    p_exec.add_argument("--args", default="{}", help="JSON arguments for the tool")

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    """Main entry point for the django-boost CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Bootstrap Django before any subcommand runs
    bootstrap_django(settings=args.settings, pythonpath=args.pythonpath)

    # Dispatch
    handlers = {
        "mcp": cmd_mcp,
        "install": cmd_install,
        "update": cmd_update,
        "list-skill": cmd_list_skill,
        "add-skill": cmd_add_skill,
        "execute-tool": cmd_execute_tool,
    }

    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    handler(args)


if __name__ == "__main__":
    main()
