"""Extraction's traversal cost, pinned so a new full pass cannot land unnoticed.

Measured, not asserted from reading: on this tree extraction reaches each node
1.69-1.91 times, because `lambda_nodes` descends the whole module a second time
after the main visitor pass. That second pass has no measurable wall-clock cost
(40 interleaved trials, difference inside one standard deviation), so it is
pinned here rather than removed. See
docs/superpowers/plans/2026-07-29-extraction-enforcer-gaps.md.
"""

from __future__ import annotations

import ast
import collections
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from humansays.analysis import extract, parse_module

if TYPE_CHECKING:
    from collections.abc import Iterator

    from humansays.facts.module import ModuleFacts

# Interned singletons: one ast.Load object stands in for every load context in
# the file, so counting it by identity is meaningless.
SINGLETONS = (ast.expr_context, ast.operator, ast.boolop, ast.unaryop, ast.cmpop)

MAX_REACHES_PER_NODE = 2.5

SAMPLES = (
    'src/humansays/analysis/extraction.py',
    'src/humansays/rules/solid/class_shape.py',
    'src/humansays/application.py',
    'tests/golden/poc-parity/corpus/poc/rules.py',
)


def reaches_per_node(path: Path) -> float:
    """Mean number of times extraction reaches each node of `path`'s tree.

    Patches `ast.iter_fields` and nothing else: it is the one primitive both
    traversal paths bottom out in, since `ast.iter_child_nodes` is built on it
    and `ast.NodeVisitor.generic_visit` calls it directly. Patching
    `iter_child_nodes` instead would miss the function visitor, which is most of
    the work; patching both would double-count.
    """
    parsed = parse_module(path)
    # This dict keeps every node alive, so a recycled id() from a short-lived
    # temporary AST cannot be mistaken for a repeat visit.
    nodes = {
        id(node): node
        for node in ast.walk(parsed.tree)
        if not isinstance(node, SINGLETONS)
    }
    reaches: collections.Counter[int] = collections.Counter()
    real_iter_fields = ast.iter_fields

    def counting_iter_fields(node: ast.AST) -> Iterator[tuple[str, object]]:
        for name, value in real_iter_fields(node):
            if isinstance(value, ast.AST):
                if id(value) in nodes:
                    reaches[id(value)] += 1

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST) and id(item) in nodes:
                        reaches[id(item)] += 1

            yield name, value

    ast.iter_fields = counting_iter_fields
    try:
        extract(parsed)
    finally:
        ast.iter_fields = real_iter_fields

    assert reaches, f'the instrument recorded nothing for {path}'
    return sum(reaches.values()) / len(reaches)


@pytest.mark.parametrize('sample', SAMPLES)
def test_extraction_does_not_add_a_traversal(sample: str) -> None:
    ratio = reaches_per_node(Path(sample))
    assert ratio <= MAX_REACHES_PER_NODE, (
        f'{sample}: extraction now reaches each node {ratio:.2f} times, over the '
        f'{MAX_REACHES_PER_NODE} ceiling. Something added a pass over the tree.'
    )


def test_the_measurement_would_notice_an_added_traversal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A ceiling only means something if breaching it is detectable.

    Without this, an instrument that silently stopped counting would leave every
    assertion above passing. Mirrors test_fact_model.py's
    test_the_walk_would_find_a_node_if_one_were_there.
    """
    from humansays.analysis import extraction

    real_extract = extraction.ModuleExtractor.extract

    def extract_with_a_spurious_walk(
        self: extraction.ModuleExtractor,
    ) -> ModuleFacts:
        result = real_extract(self)
        for _ in ast.walk(self.module.tree):  # the regression being guarded against
            pass

        return result

    monkeypatch.setattr(
        extraction.ModuleExtractor,
        'extract',
        extract_with_a_spurious_walk,
    )
    ratio = reaches_per_node(Path('src/humansays/application.py'))
    assert ratio > MAX_REACHES_PER_NODE, (
        f'an extra full walk only moved the ratio to {ratio:.2f}, which is under '
        f'the {MAX_REACHES_PER_NODE} ceiling -- the ceiling cannot catch a new pass'
    )
