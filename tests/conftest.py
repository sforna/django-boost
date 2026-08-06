"""
Test configuration and fixtures for django-boost.
"""

import os
import sys

import django
import pytest

# Ensure the source directory is in the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
django.setup()


@pytest.fixture
def temp_dir(tmp_path):
    """A temporary directory for file-based tests."""
    return tmp_path


@pytest.fixture
def project_root(tmp_path):
    """Simulate a Django project root with manage.py."""
    manage_py = tmp_path / "manage.py"
    manage_py.write_text("#!/usr/bin/env python\nimport sys\nif __name__ == '__main__':\n    sys.exit()\n")
    return tmp_path
