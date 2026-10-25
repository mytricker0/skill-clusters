"""Shared pytest fixtures for the skill-clusters test suite."""

import os
import shutil
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

FIXTURES = os.path.join(REPO_ROOT, "tests", "fixtures")


@pytest.fixture
def fixtures_dir():
    return FIXTURES


@pytest.fixture
def run_cli():
    """Run the installed CLI as a subprocess and capture output.

    Returns (exit_code, stdout, stderr).
    """

    def _run(*args, cwd=None):
        proc = subprocess.run(
            ["skill-clusters", *args],
            capture_output=True,
            text=True,
            cwd=cwd or REPO_ROOT,
        )
        return proc.returncode, proc.stdout, proc.stderr

    return _run


@pytest.fixture
def fixtures_copy(tmp_path):
    """A writable copy of the fixtures tree for tests that mutate skills."""
    dest = tmp_path / "fixtures"
    shutil.copytree(FIXTURES, dest)
    return str(dest)
