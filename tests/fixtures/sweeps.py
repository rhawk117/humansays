"""File sweeps that cannot come back empty without saying so.

A test that walks a tree and finds no offenders passes. So does one that walked
nothing at all, and from outside the two are the same green tick. Nothing
passive distinguishes them: the analyzer's output is unchanged either way, and
coverage cannot see it, because a sweep reads source files as *data* -- its
input set halving does not move a covered line by one.

That has now shipped twice in this repository. `test_no_two_adapters_share_a_
sort_key` surveyed a corpus that never fired `encap.class_shared_state`, one of
the two HS004 registrations it exists to compare. The interpreter-version
survey in `test_analysis_confinement.py` named `signals`, that package became
`rules`, and `rglob` over a directory that does not exist yields nothing rather
than raising.

So the sweeps do not live at their call sites. Every one of them comes through
here, and an empty result is an error rather than a result. The thin-corpus
version of a sweep is not something to remember not to write; it does not
survive the call.

CLAUDE.md "Always" 14 is the rule this module implements.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def matching(directory: Path, pattern: str) -> list[Path]:
    """Every file under `directory` matching `pattern`, sorted, never empty.

    Raises rather than returning `[]`, because the caller is about to conclude
    something from the absence of a match and cannot tell that case apart from
    having looked nowhere.
    """
    found = sorted(directory.rglob(pattern))
    if not found:
        raise AssertionError(
            f'{directory} contains no {pattern}, so the sweep about to run over '
            f'it would examine nothing and pass. Either the path is stale -- a '
            f'renamed or moved package is the usual cause -- or the caller is '
            f'asking for a corpus that no longer exists.'
        )

    return found


def python_sources(root: Path, *packages: str) -> list[Path]:
    """Every `*.py` under each named package of `root`, sorted, never empty.

    Each package is checked separately. A survey over several packages where
    one has been renamed still returns files, so asserting on the total would
    miss exactly the failure this exists to catch.
    """
    if not packages:
        return matching(root, '*.py')

    return [path for package in packages for path in matching(root / package, '*.py')]
