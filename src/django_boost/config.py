"""
Default configuration for Django Boost.

All settings can be overridden in Django's settings.py by prefixing with BOOST_.
For example, to disable Boost, set BOOST_ENABLED = False in your settings.
"""

from django.conf import settings as django_settings

DEFAULTS = {
    # Master switch — set BOOST_ENABLED=False to disable all Boost functionality.
    "enabled": True,
    # Browser logs watcher — enable/disable browser log collection.
    "browser_logs_watcher": True,
    # Browser log levels to capture.
    "browser_log_levels": ["error", "warning", "info", "debug"],
    # Project rules configuration.
    "rules_enabled": True,
    "rules_scoped_guidelines": False,
    # Excluded guidelines (list of names to skip).
    "guidelines_exclude": [],
    # Excluded skills (list of names to skip).
    "skills_exclude": [],
    # Executable paths (None = auto-detect).
    "executable_paths": {
        "python": None,
        "pip": None,
        "npm": None,
        "current_directory": None,
    },
    # Tinker tool — disabled by default for safety.
    "tinker_tool_enabled": False,
    # MCP tool exclusion/inclusion.
    "mcp_tools_exclude": [],
    "mcp_tools_include": [],
    # MCP tool execution timeout (seconds).
    "mcp_tool_timeout": 30,
    # Agent-specific paths (override defaults).
    "agents": {},
    # Hosted docs API URL.
    "hosted_api_url": "https://boost.laravel.com",
}


def get_config(key: str, default=None):
    """Get a Boost configuration value from Django settings.

    Looks for BOOST_<KEY> in Django settings, falls back to DEFAULTS.
    """
    django_key = f"BOOST_{key.upper()}"
    return getattr(django_settings, django_key, DEFAULTS.get(key.lower(), default))
