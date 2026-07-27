"""Syntax helpers.

Small readers over single nodes: resolve a dotted name or import alias, decide
whether an expression builds a mutable collection, measure a span, and count the
executable lines inside one. Nothing here holds state or emits a finding.
"""

import ast
from collections.abc import Iterable

from humansays.analysis.models import FunctionNode, ParsedModule
from humansays.const import BOOL_NAMES, BOUNDARY_MODULES, UNPARSE_LIMIT
from humansays.findings.models import Location

MUTABLE_LITERALS = (
    ast.Dict,
    ast.List,
    ast.Set,
    ast.DictComp,
    ast.ListComp,
    ast.SetComp,
)


def dotted_name(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f'{parent}.{node.attr}' if parent else node.attr

    return None


def root_name(node: ast.AST) -> str | None:
    while isinstance(node, (ast.Attribute, ast.Subscript)):
        node = node.value

    return node.id if isinstance(node, ast.Name) else None


def assigned_names(node: ast.Assign | ast.AnnAssign) -> list[tuple[str, ast.AST]]:
    value = getattr(node, 'value', None)
    if value is None:
        return []

    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    return [(target.id, value) for target in targets if isinstance(target, ast.Name)]


def resolve_alias(name: str, aliases: dict[str, str]) -> str:
    head, separator, tail = name.partition('.')
    replacement = aliases.get(head, head)
    return replacement + (separator + tail if separator else '')


def is_mutable_expression(
    node: ast.AST,
    aliases: dict[str, str],
    constructors: frozenset[str],
) -> bool:
    if isinstance(node, MUTABLE_LITERALS):
        return True

    if not isinstance(node, ast.Call):
        return False

    constructor = dotted_name(node.func)
    return constructor is not None and resolve_alias(constructor, aliases) in constructors


def annotation_is_bool(node: ast.AST | None) -> bool:
    return dotted_name(node) in BOOL_NAMES


def referenced_names(node: ast.AST) -> set[str]:
    return {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}


def contains_raise(nodes: Iterable[ast.AST]) -> bool:
    return any(isinstance(child, ast.Raise) for node in nodes for child in ast.walk(node))


def decorator_names(node: FunctionNode) -> tuple[str, ...]:
    names = []
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator

        if name := dotted_name(target):
            names.append(name)

    return tuple(names)


def classify_boundary(name: str) -> str | None:
    for boundary, modules in BOUNDARY_MODULES.items():
        matches = (name == module or name.startswith(f'{module}.') for module in modules)
        if any(matches):
            return boundary

    return None


def node_span(node: ast.AST) -> tuple[int, int]:
    line = getattr(node, 'lineno', 1)
    maybe_endline_no = getattr(node, 'end_lineno', None)
    return (line, maybe_endline_no or line)


def location_of(symbol: str, node: ast.AST) -> Location:
    line, end_line = node_span(node)
    return Location(symbol, line, end_line)


def snippet(node: ast.AST) -> str:
    text = ast.unparse(node)
    if len(text) <= UNPARSE_LIMIT:
        return text

    return f'{text[:UNPARSE_LIMIT]}...'


def docstring_span(node: ast.AST) -> range:
    body = getattr(node, 'body', [])
    if not body:
        return range(0)

    first = body[0]
    if not isinstance(first, ast.Expr) or not isinstance(first.value, ast.Constant):
        return range(0)

    if not isinstance(first.value.value, str):
        return range(0)

    start, end = node_span(first)
    return range(start, end + 1)


def code_line_count(module: ParsedModule, node: ast.AST) -> int:
    """Executable lines: the span minus blanks, comment-only lines, and the docstring."""
    start, end = node_span(node)
    skipped = docstring_span(node)
    lines = module.lines
    counted = 0
    for number in range(start, min(end, len(lines)) + 1):
        text = lines[number - 1].strip()
        if text and not text.startswith('#') and number not in skipped:
            counted += 1

    return counted
