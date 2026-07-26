"""The declared version, the installed metadata, and `--version` must agree.

`humansays --version` reads `importlib.metadata.version('humansays')`
(`config/loading.py:122`), not a constant in the source, so a stale install
reports a version the source no longer declares. That silent drift is what
these assert against.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from importlib.metadata import version as installed_version
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def declared_version() -> str:
    document = tomllib.loads((REPO_ROOT / 'pyproject.toml').read_text(encoding='utf-8'))
    return str(document['project']['version'])


def test_installed_metadata_matches_pyproject() -> None:
    assert installed_version('humansays') == declared_version()


def test_cli_version_flag_matches_installed_metadata() -> None:
    result = subprocess.run(
        [sys.executable, '-m', 'humansays', '--version'],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == f'humansays {installed_version("humansays")}'
