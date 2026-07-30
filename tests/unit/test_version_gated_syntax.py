"""Extraction against grammar that does not exist on every supported interpreter.

`requires-python` is ">=3.11" and CI runs a 3.11-3.14 matrix, but until this
module existed nothing in the suite used syntax newer than 3.11. The matrix
proved the old tests pass everywhere; it did not prove the parser divergences
were handled, because nothing exercised them.

Each test skips below the version that introduced its syntax, so the file is
collected everywhere and asserts only what the running interpreter can parse.
The snippets live in tests/fixtures/sources.py as strings, unparsed at import.
"""

from __future__ import annotations

import ast
import dataclasses
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from humansays.analysis.extraction import extract
from humansays.analysis.models import ParsedModule
from tests.fixtures import sources

if TYPE_CHECKING:
    from humansays.facts.module import ModuleFacts

needs_312 = pytest.mark.skipif(
    sys.version_info < (3, 12),
    reason='PEP 695 type parameters and PEP 701 f-strings arrived in 3.12',
)
needs_313 = pytest.mark.skipif(
    sys.version_info < (3, 13),
    reason='PEP 696 type parameter defaults arrived in 3.13',
)


def facts_for(source: str, name: str = '<snippet>') -> ModuleFacts:
    return extract(ParsedModule(Path(name), source, ast.parse(source)))


def reached_nodes(value: Any, seen: set[int] | None = None) -> list[str]:
    """Names of any `ast` nodes reachable from `value`.

    Local rather than shared with test_fact_model.py: `tests` is not a package,
    so importing across test modules would rely on namespace-package resolution.
    """
    seen = set() if seen is None else seen
    if id(value) in seen:
        return []

    seen.add(id(value))
    found = [type(value).__name__] if isinstance(value, ast.AST) else []
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        for field in dataclasses.fields(value):
            found.extend(reached_nodes(getattr(value, field.name), seen))

    elif isinstance(value, dict):
        for key, item in value.items():
            found.extend(reached_nodes(key, seen))
            found.extend(reached_nodes(item, seen))

    elif isinstance(value, (list, tuple, set, frozenset)):
        for item in value:
            found.extend(reached_nodes(item, seen))

    return found


class TestTypeParameters:
    @needs_312
    def test_a_type_parameter_is_not_counted_as_an_argument(self) -> None:
        """`def transform[T](value)` takes one argument, not two.

        This is the divergence with teeth: `type_params` sits next to `args` on
        the FunctionDef, so a signature reader that is not explicit about which
        list it walks will silently inflate every generic function's argument
        count, and the argument-count rules fire on the difference.
        """
        facts = facts_for(sources.GENERIC_FUNCTION)
        function = facts.functions[0]
        assert function.name == 'transform'
        assert tuple(function.signature.parameters) == ('value',)

    @needs_312
    def test_a_generic_class_and_its_generic_method_are_found(self) -> None:
        facts = facts_for(sources.GENERIC_CLASS)
        assert [klass.location.symbol for klass in facts.classes] == ['Store']
        methods = facts.classes[0].methods
        assert [method.name for method in methods] == ['put', 'get']
        assert tuple(methods[1].signature.parameters) == ('self', 'fallback')

    @needs_313
    def test_a_type_parameter_default_is_not_counted_as_an_argument(self) -> None:
        facts = facts_for(sources.TYPEVAR_DEFAULT)
        function = facts.functions[0]
        assert function.name == 'pick'
        assert tuple(function.signature.parameters) == ('value',)


class TestStatementsAddedAfter311:
    @needs_312
    def test_a_type_alias_does_not_hide_what_follows_it(self) -> None:
        """`ast.TypeAlias` is neither Assign nor AnnAssign.

        Module-scope collection dispatches on those two, so a `type X = ...`
        statement is skipped -- correctly. What matters is that skipping it does
        not disturb the definitions after it.
        """
        facts = facts_for(sources.TYPE_ALIAS_MODULE)
        assert [function.name for function in facts.functions] == ['use']
        assert facts.line_count == 8


class TestPep701FStrings:
    @needs_312
    def test_quotes_reused_inside_an_fstring_do_not_break_spans(self) -> None:
        """PEP 701 changed JoinedStr structure and column offsets.

        `analysis/syntax.py` reads spans off nodes, so the assertion that earns
        its place is on the location, not merely that extraction returned.
        """
        facts = facts_for(sources.NESTED_QUOTE_FSTRING)
        function = facts.functions[0]
        assert function.name == 'render'
        assert function.location.line == 2
        assert function.location.end_line == 3


class TestFactsStayCleanOnNewSyntax:
    @needs_312
    @pytest.mark.parametrize(
        'name',
        [
            'GENERIC_FUNCTION',
            'GENERIC_CLASS',
            'TYPE_ALIAS_MODULE',
            'NESTED_QUOTE_FSTRING',
        ],
    )
    def test_no_ast_node_leaks_through_newer_grammar(self, name: str) -> None:
        """Newer grammar adds fields; a field copied wholesale would leak a node."""
        facts = facts_for(getattr(sources, name))
        assert reached_nodes(facts) == []
