"""The ast/tokenize contract enumerates its source modules by hand, so it fails
open: a new module outside `humansays.analysis` is simply not covered, and
`lint-imports` still reports the contract as kept.

`tests/integration/test_analysis_confinement.py` is the backstop that catches
the offending import itself. This test keeps the contract from quietly
weakening underneath it.
"""

from __future__ import annotations

import configparser
from typing import TYPE_CHECKING

from tests.fixtures.sweeps import python_sources

if TYPE_CHECKING:
    from pathlib import Path

CONTRACT = 'importlinter:contract:ast-confined-to-analysis'


def listed_modules() -> set[str]:
    config = configparser.ConfigParser()
    config.read('.importlinter.ini')
    return set(config[CONTRACT]['source_modules'].split())


def module_name(path: Path, src_root: Path) -> str:
    parts = path.relative_to(src_root.parent).with_suffix('').parts
    if parts[-1] == '__init__':
        parts = parts[:-1]

    return '.'.join(parts)


def test_contract_covers_every_module_outside_analysis(src_root: Path) -> None:
    expected = {
        module_name(path, src_root)
        for path in python_sources(src_root)
        if path.relative_to(src_root).parts[0] != 'analysis'
    }
    # The root package is deliberately absent from the contract: it re-exports
    # only, and listing it would shadow the per-module entries below it.
    expected.discard('humansays')

    missing = sorted(expected - listed_modules())
    assert not missing, (
        f'{CONTRACT} does not list {missing}. The contract passes without '
        f'covering them, so add each to source_modules in .importlinter.ini.'
    )


def test_contract_lists_nothing_that_no_longer_exists(src_root: Path) -> None:
    """A stale entry does not weaken enforcement, but it does hide that the
    list is unmaintained, which is what lets a missing entry go unnoticed."""
    real = {module_name(path, src_root) for path in python_sources(src_root)}
    stale = sorted(listed_modules() - real)
    assert not stale, f'{CONTRACT} lists modules that do not exist: {stale}'
