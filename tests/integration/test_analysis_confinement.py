"""The `ast`/`tokenize` ban is a package-layout constraint, so it is asserted
against the real source tree rather than a snippet.

`lint-imports` (`.importlinter.ini`) is the primary enforcer; this test is the
second one.
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
