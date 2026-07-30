"""Package-layout constraints, asserted against the real source tree rather
than a snippet.

Two claims live here. The `ast`/`tokenize` ban, whose primary enforcer is
`lint-imports` (`.importlinter.ini`) with this test as the second one. And the
normalization boundary: interpreter differences are `humansays.analysis`'s
problem, so nothing downstream may branch on the running version.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def test_ast_and_tokenize_are_confined_to_analysis(src_root: Path) -> None:
    offenders = []
    for path in sorted(src_root.rglob('*.py')):
        relative = path.relative_to(src_root)
        if relative.parts[0] == 'analysis':
            continue
        tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = {alias.name for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {node.module} if node.module else set()
            else:
                continue
            if names & {'ast', 'tokenize'}:
                offenders.append((str(relative), names))
    assert not offenders


def test_analysis_and_rules_do_not_import_each_other(src_root: Path) -> None:
    """Extraction and evaluation are siblings that meet only at `humansays.facts`.

    `lint-imports` is the primary enforcer: the `layers` contract writes them as
    `humansays.analysis | humansays.rules`, and the pipe bans the import in
    both directions. This is the second enforcer, and it exists for symmetry --
    the `ast` ban above already had two, and this boundary is the one the
    extraction/evaluation split was carried out to create.
    """
    banned = {'analysis': 'humansays.rules', 'rules': 'humansays.analysis'}
    offenders = []
    for package, forbidden in banned.items():
        for path in sorted((src_root / package).rglob('*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = {alias.name for alias in node.names}
                elif isinstance(node, ast.ImportFrom):
                    names = {node.module} if node.module else set()
                else:
                    continue

                if any(
                    name == forbidden or name.startswith(f'{forbidden}.')
                    for name in names
                ):
                    offenders.append((str(path.relative_to(src_root)), sorted(names)))

    assert not offenders


def test_facts_and_signals_never_branch_on_interpreter_version(
    src_root: Path,
) -> None:
    """`humansays.analysis` owns interpreter differences; downstream never sees them.

    Zero occurrences today, so this pins a property rather than fixing a bug.
    It is worth pinning because the first `sys.version_info` to appear in
    `facts` or `signals` would put a parser detail into the layer whose whole
    purpose is not to have one, and it would do so in a one-line diff.
    """
    offenders = [
        f'{path.relative_to(src_root)}:{number}'
        for package in ('facts', 'signals')
        for path in sorted((src_root / package).rglob('*.py'))
        for number, line in enumerate(
            path.read_text(encoding='utf-8').splitlines(), start=1
        )
        if 'version_info' in line
    ]
    assert not offenders
