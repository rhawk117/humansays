"""Fixture material that has to exist as a real file on disk.

The CLI accepts paths, not strings, so the snippets it scans have to be
written somewhere. Writing them into `tmp_path` per test replaces the
committed duplicate that used to live at `tests/fixture_module.py`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.fixtures import sources

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def smelly_module_path(tmp_path: Path) -> Path:
    """`sources.SMELLY_MODULE` written to disk so the CLI can be pointed at it."""
    path = tmp_path / 'smelly_module.py'
    path.write_text(sources.SMELLY_MODULE, encoding='utf-8')
    return path


@pytest.fixture
def config_toml_path(tmp_path: Path) -> Path:
    """`sources.CONFIG_TOML` written to disk for `--config` to load."""
    path = tmp_path / 'humansays.toml'
    path.write_text(sources.CONFIG_TOML, encoding='utf-8')
    return path
