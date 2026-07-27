"""Filesystem anchors, resolved once instead of by hand in each test module."""

from __future__ import annotations

from pathlib import Path

import pytest

_TESTS_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope='session')
def repo_root() -> Path:
    """The repository checkout root."""
    return _TESTS_ROOT.parent


@pytest.fixture(scope='session')
def src_root() -> Path:
    """The installed package's source directory, `src/humansays`."""
    return _TESTS_ROOT.parent / 'src' / 'humansays'


@pytest.fixture(scope='session')
def baseline_path() -> Path:
    """The frozen self-scan baseline the golden tests assert against."""
    return _TESTS_ROOT / 'golden' / 'self-scan-baseline.json'
