"""Enforcement tests for the phase scope guard.

Named by ``docs/process/scope-guard.md`` and by ``agent-protocol.md`` §4a.
If these do not pass, the claim that phase scope is enforced is unsupported.

The eight cases run the real ``check_scope.py`` against a real temporary git
repository, because the guard's whole subject is git state. The ninth is a
unit test on glob translation: ``*`` crossing ``/`` is the bash-era defect
that let ``src/humansays/**`` match at any depth.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD_SOURCE = REPO_ROOT / 'scripts' / 'check_scope.py'
PHASE = 'test-phase'
ALLOWLIST = f'docs/phases/{PHASE}/allowed-paths.txt'

# Mirrors the shape of a real phase allowlist: a package glob, the phase's own
# directory, the guard itself (as 01-review lists it), and one deny line.
PATTERNS = """\
src/pkg/**
docs/phases/test-phase/**
scripts/check_scope.py
!src/pkg/analysis/signature*
"""


def git(repo: Path, *args: str) -> None:
    subprocess.run(  # noqa: S603
        ['git', *args],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def write(repo: Path, relative: str, text: str) -> None:
    target = repo / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8')


def commit(repo: Path, message: str) -> None:
    git(repo, 'add', '-A')
    git(repo, 'commit', '-m', message)


def run_guard(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [sys.executable, 'scripts/check_scope.py', PHASE, '--base', 'base'],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A git repository with a `base` ref, a copy of the guard, and content.

    `README.md` is tracked and outside the allowlist so case 4 has something
    legitimate to edit; unchanged files are never reported.
    """
    root = tmp_path / 'scope-repo'
    root.mkdir()
    git(root, 'init', '--initial-branch=main')
    git(root, 'config', 'user.email', 'guard@test.invalid')
    git(root, 'config', 'user.name', 'Guard Test')
    git(root, 'config', 'commit.gpgsign', 'false')

    (root / 'scripts').mkdir()
    shutil.copy2(GUARD_SOURCE, root / 'scripts' / 'check_scope.py')
    write(root, ALLOWLIST, PATTERNS)
    write(root, 'src/pkg/keep.py', 'VALUE = 1\n')
    write(root, 'README.md', 'base\n')

    commit(root, 'base')
    git(root, 'branch', 'base')
    return root


def test_committed_change_to_denied_path_is_blocked(repo: Path) -> None:
    write(repo, 'src/pkg/analysis/signature_reader.py', 'X = 1\n')
    commit(repo, 'touch denied path')

    result = run_guard(repo)

    assert result.returncode == 1
    assert 'src/pkg/analysis/signature_reader.py' in result.stderr
    assert 'explicitly denied' in result.stderr
    assert '[committed]' in result.stderr


def test_staged_file_outside_allowlist_is_blocked(repo: Path) -> None:
    write(repo, 'tools/extra.py', 'X = 1\n')
    git(repo, 'add', 'tools/extra.py')

    result = run_guard(repo)

    assert result.returncode == 1
    assert 'tools/extra.py' in result.stderr
    assert 'outside the allowlist' in result.stderr
    assert '[staged]' in result.stderr


def test_untracked_file_outside_allowlist_is_blocked(repo: Path) -> None:
    write(repo, 'tools/extra.py', 'X = 1\n')

    result = run_guard(repo)

    assert result.returncode == 1
    assert 'tools/extra.py' in result.stderr
    assert '[untracked]' in result.stderr


def test_unstaged_edit_outside_allowlist_is_blocked(repo: Path) -> None:
    write(repo, 'README.md', 'edited\n')

    result = run_guard(repo)

    assert result.returncode == 1
    assert 'README.md' in result.stderr
    assert '[unstaged]' in result.stderr


def test_allowlist_widened_alongside_other_changes_is_blocked(repo: Path) -> None:
    write(repo, ALLOWLIST, PATTERNS + 'tools/**\n')
    write(repo, 'src/pkg/keep.py', 'VALUE = 2\n')
    commit(repo, 'widen allowlist and change code')

    result = run_guard(repo)

    assert result.returncode == 1
    assert 'allowlist widened in a mixed commit' in result.stderr


def test_edit_to_the_guard_itself_is_blocked(repo: Path) -> None:
    guard = repo / 'scripts' / 'check_scope.py'
    guard.write_text(
        guard.read_text(encoding='utf-8') + '\n# tampered\n', encoding='utf-8'
    )
    commit(repo, 'edit the guard')

    result = run_guard(repo)

    assert result.returncode == 1
    assert 'scripts/check_scope.py' in result.stderr
    assert 'not editable during a phase' in result.stderr


def test_legitimate_in_scope_change_passes(repo: Path) -> None:
    write(repo, 'src/pkg/keep.py', 'VALUE = 2\n')
    commit(repo, 'in-scope change')

    result = run_guard(repo)

    assert result.returncode == 0
    assert 'scope ok' in result.stdout


def test_isolated_allowlist_widening_is_permitted(repo: Path) -> None:
    write(repo, ALLOWLIST, PATTERNS + 'tools/**\n')
    commit(repo, 'widen allowlist, nothing else')

    result = run_guard(repo)

    assert result.returncode == 0
    assert 'scope ok' in result.stdout


@pytest.fixture(scope='module')
def guard() -> ModuleType:
    """Load the guard by path; `scripts` is not on `.pytest.toml` pythonpath."""
    spec = importlib.util.spec_from_file_location('check_scope', GUARD_SOURCE)
    if spec is None or spec.loader is None:
        pytest.fail(f'could not load {GUARD_SOURCE}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ('pattern', 'path', 'matches'),
    [
        ('src/*', 'src/a.py', True),
        ('src/*', 'src/pkg/a.py', False),
        ('src/**', 'src/a.py', True),
        ('src/**', 'src/pkg/deep/a.py', True),
        ('src/humansays/**', 'src/other/a.py', False),
        ('src/?.py', 'src/a.py', True),
        ('src/?.py', 'src/ab.py', False),
    ],
)
def test_star_stays_within_a_segment_and_doublestar_crosses(
    guard: ModuleType,
    pattern: str,
    path: str,
    matches: bool,  # noqa: FBT001
) -> None:
    assert bool(guard.glob_to_regex(pattern).match(path)) is matches
