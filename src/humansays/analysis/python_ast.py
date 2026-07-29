"""Reading facts off the tree.

``syntax`` reads individual nodes. This module describes whole definitions:
what a signature declares, what attributes a class body reserves, where the
lambdas are, which bindings are mutable. Everything here returns facts, so
``rules`` can judge them without touching ``ast`` itself.

``body_visitor`` owns the other half, walking a single function body. The
module-size rule lives here rather than in ``rules`` because it needs nothing
but the parse result.
"""

import ast
from collections.abc import Iterable
from operator import itemgetter

from humansays.analysis.body_visitor import FunctionVisitor
from humansays.analysis.models import (
    FunctionFacts,
    FunctionNode,
    FunctionTarget,
    MutableBinding,
    ParsedModule,
    ScopeContext,
    Signature,
)
from humansays.analysis.syntax import (
    annotation_is_bool,
    assigned_names,
    code_line_count,
    decorator_names,
    dotted_name,
    is_mutable_expression,
    location_of,
    node_span,
    root_name,
    snippet,
)
from humansays.catalog import build_finding
from humansays.config.models import ModuleThresholds
from humansays.const import (
    CLASS_VAR_NAMES,
    CLUSTER_MINIMUM,
    NON_STRUCTURAL_PREFIXES,
)
from humansays.enums import SignalName
from humansays.factories import string_set_map
from humansays.facts.values import frozen_evidence
from humansays.findings.models import Finding, Location, Observation

FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)
STATIC_DECORATOR = 'staticmethod'


def assigned_slots(statement: ast.stmt) -> set[str] | None:
    if not isinstance(statement, ast.Assign):
        return None
    slot_targets = (
        isinstance(target, ast.Name) and target.id == '__slots__'
        for target in statement.targets
    )
    if not any(slot_targets):
        return None
    if not isinstance(statement.value, (ast.List, ast.Set, ast.Tuple)):
        return set()
    return {
        item.value
        for item in statement.value.elts
        if isinstance(item, ast.Constant) and isinstance(item.value, str)
    }


def annotated_attribute(statement: ast.AnnAssign) -> set[str]:
    if not isinstance(statement.target, ast.Name):
        return set()

    if dotted_name(statement.annotation) in CLASS_VAR_NAMES:
        return set()

    return {statement.target.id}


def plain_attributes(statement: ast.Assign, method_names: set[str]) -> set[str]:
    if isinstance(statement.value, ast.Name) and statement.value.id in method_names:
        return set()

    return {
        target.id
        for target in statement.targets
        if isinstance(target, ast.Name) and not target.id.isupper()
    }


def declared_class_attributes(node: ast.ClassDef) -> set[str]:
    attributes: set[str] = set()
    method_names = {
        statement.name for statement in node.body if isinstance(statement, FUNCTION_NODES)
    }

    for statement in node.body:
        slots = assigned_slots(statement)
        if slots is not None:
            attributes.update(slots)

        elif isinstance(statement, ast.AnnAssign):
            attributes.update(annotated_attribute(statement))

        elif isinstance(statement, ast.Assign):
            attributes.update(plain_attributes(statement, method_names))

    return attributes


def attribute_prefix_clusters(attributes: Iterable[str]) -> dict[str, tuple[str, ...]]:
    grouped = string_set_map()
    for attribute in attributes:
        prefix, separator, _ = attribute.lstrip('_').partition('_')
        if separator and prefix not in NON_STRUCTURAL_PREFIXES:
            grouped[prefix].add(attribute)

    return {
        prefix: tuple(sorted(names))
        for prefix, names in grouped.items()
        if len(names) >= CLUSTER_MINIMUM
    }


def argument_defaults(node: FunctionNode) -> dict[str, ast.AST]:
    positional = [*node.args.posonlyargs, *node.args.args]
    defaults: dict[str, ast.AST] = {}
    offset = len(node.args.defaults)
    paired = zip(
        positional[len(positional) - offset :],
        node.args.defaults,
        strict=True,
    )

    for argument, default in paired:
        defaults[argument.arg] = default

    for argument, default in zip(
        node.args.kwonlyargs,
        node.args.kw_defaults,
        strict=True,
    ):
        if default is not None:
            defaults[argument.arg] = default

    return defaults


def declared_arguments(node: FunctionNode) -> list[ast.arg]:
    arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
    if node.args.vararg:
        arguments.append(node.args.vararg)

    if node.args.kwarg:
        arguments.append(node.args.kwarg)

    return arguments


def is_typed_default_value_bool(
    argument: ast.arg,
    default: ast.AST | None,
) -> bool:
    if annotation_is_bool(argument.annotation):
        return True

    return isinstance(default, ast.Constant) and isinstance(default.value, bool)


def build_signature(node: FunctionNode) -> Signature:
    arguments = declared_arguments(node)
    defaults = argument_defaults(node)
    boolean = []
    for argument in arguments:
        default = defaults.get(argument.arg)
        if is_typed_default_value_bool(argument, default):
            boolean.append(argument.arg)

    return Signature(
        parameters=tuple(argument.arg for argument in arguments),
        boolean_parameters=tuple(boolean),
    )


def is_trivial_accessor(node: FunctionNode) -> bool:
    if len(node.body) != 1:
        return False

    statement = node.body[0]
    if isinstance(statement, ast.Return):
        value = statement.value
        return isinstance(value, ast.Attribute) and root_name(value) == 'self'

    if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
        return False

    targets = (
        statement.targets if isinstance(statement, ast.Assign) else [statement.target]
    )

    return all(
        isinstance(target, ast.Attribute) and root_name(target) == 'self'
        for target in targets
    )


def collect_aliases(tree: ast.Module) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for statement in tree.body:
        if isinstance(statement, ast.Import):
            for name in statement.names:
                aliases[name.asname or name.name.split('.', 1)[0]] = name.name

        elif isinstance(statement, ast.ImportFrom) and statement.module:
            for name in statement.names:
                aliases[name.asname or name.name] = f'{statement.module}.{name.name}'

    return aliases


def collect_module_globals(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for statement in tree.body:
        if isinstance(statement, (ast.Assign, ast.AnnAssign)):
            names.update(name for name, _ in assigned_names(statement))

    return names


def module_scale_findings(
    count: int,
    thresholds: ModuleThresholds,
) -> list[Finding]:
    if count <= thresholds.max_lines:
        return []

    location = Location('<module>', 1, max(1, count))
    observation = Observation(
        f'Module spans {count} source lines.',
        (f'configured threshold: {thresholds.max_lines}',),
    )

    return [build_finding(SignalName.HS017, location, observation)]


def is_static_method(node: FunctionNode) -> bool:
    return STATIC_DECORATOR in decorator_names(node)


def base_class_names(node: ast.ClassDef) -> tuple[str, ...]:
    return tuple(dotted_name(base) or snippet(base) for base in node.bases)


def lambda_nodes(tree: ast.Module) -> list[ast.Lambda]:
    found: list[tuple[int, int, ast.Lambda]] = []
    position = 0

    def descend(node: ast.AST, depth: int) -> None:
        nonlocal position
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Lambda):
                found.append((depth, position, child))

            position += 1
            descend(child, depth + 1)

    descend(tree, 1)
    return [node for _, _, node in sorted(found, key=itemgetter(0, 1))]


def mutable_bindings(
    body: list[ast.stmt],
    aliases: dict[str, str],
    constructors: frozenset[str],
) -> list[MutableBinding]:
    bindings: list[MutableBinding] = []
    for statement in body:
        if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
            continue

        line, end_line = node_span(statement)
        bindings.extend(
            MutableBinding(
                name=name,
                line=line,
                end_line=end_line,
                constructor=type(value).__name__,
            )
            for name, value in assigned_names(statement)
            if is_mutable_expression(value, aliases, constructors)
        )

    return bindings


def class_state_attributes(
    node: ast.ClassDef,
    methods: Iterable[FunctionFacts],
) -> set[str]:
    return declared_class_attributes(node) | {
        attribute for method in methods for attribute in method.self_usage.fields_written
    }


def build_function_facts(
    module: ParsedModule,
    target: FunctionTarget,
    context: ScopeContext,
) -> FunctionFacts:
    node = target.node
    signature = build_signature(node)
    visitor = FunctionVisitor(signature.parameters, context)
    for statement in node.body:
        visitor.visit(statement)

    visitor.body.code_lines = code_line_count(module, node)

    return FunctionFacts(
        signature=Signature(
            parameters=signature.parameters,
            boolean_parameters=signature.boolean_parameters,
            validated_parameters=frozen_evidence(visitor.validated),
        ),
        body=visitor.body.freeze(),
        self_usage=visitor.usage.freeze(),
        location=location_of(target.qualified_name, node),
        trivial_accessor=is_trivial_accessor(node),
        static_method=is_static_method(node),
    )
