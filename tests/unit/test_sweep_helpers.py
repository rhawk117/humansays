"""The sweep helpers refuse an empty corpus, which is what every caller leans on.

`tests/fixtures/sweeps.py` is the single point where the suite's file sweeps
turn a directory into a file list. Every survey that walks the tree calls it,
and none of them re-checks the result, so the guarantee has to hold here or
nowhere. A helper that quietly returned `[]` would restore the exact failure it
was written to remove, in every caller at once.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.fixtures.sweeps import entries, matching, python_sources

if TYPE_CHECKING:
    from pathlib import Path


def test_matching_raises_when_the_directory_does_not_exist(tmp_path: Path) -> None:
    """The renamed-package case. `rglob` yields nothing rather than raising."""
    with pytest.raises(AssertionError, match='contains no'):
        matching(tmp_path / 'renamed-away', '*.py')


def test_matching_raises_when_the_directory_holds_nothing_matching(
    tmp_path: Path,
) -> None:
    (tmp_path / 'notes.md').write_text('', encoding='utf-8')
    with pytest.raises(AssertionError, match='contains no'):
        matching(tmp_path, '*.py')


def test_matching_returns_sorted_paths(tmp_path: Path) -> None:
    for name in ('b.py', 'a.py'):
        (tmp_path / name).write_text('', encoding='utf-8')

    assert [path.name for path in matching(tmp_path, '*.py')] == ['a.py', 'b.py']


def test_python_sources_checks_each_package_separately(tmp_path: Path) -> None:
    """The multi-package survey is where a total-count check would fail.

    `facts` still holding files is what made the `signals` rename invisible:
    the sweep returned plenty of paths, just none from the package that had
    moved. So an empty package is an error even when its siblings are full.
    """
    (tmp_path / 'facts').mkdir()
    (tmp_path / 'facts' / 'values.py').write_text('', encoding='utf-8')

    with pytest.raises(AssertionError, match='rules'):
        python_sources(tmp_path, 'facts', 'rules')


def test_python_sources_sweeps_the_root_when_no_package_is_named(
    tmp_path: Path,
) -> None:
    (tmp_path / 'nested').mkdir()
    (tmp_path / 'nested' / 'module.py').write_text('', encoding='utf-8')

    assert [path.name for path in python_sources(tmp_path)] == ['module.py']


def test_entries_returns_sorted_keys() -> None:
    assert entries({'poc': 1, 'django': 2}, 'a table') == ['django', 'poc']


def test_entries_refuses_an_empty_table() -> None:
    with pytest.raises(AssertionError, match=r'manifest\.toml'):
        entries({}, "manifest.toml's [groups]")
