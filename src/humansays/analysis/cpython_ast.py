"""Function and class shape, body walking, and the module-size rule.

``syntax`` reads individual nodes; this module describes whole definitions —
what a signature declares, what attributes a class body reserves — and walks one
function body recording what it nests, branches on, mutates, imports, and
touches.

The module-size rule lives here rather than in ``rules`` because it needs
nothing but the parse result.
"""

import ast
from collections.abc import Iterable

from humansays.catalog import build_finding
from humansays.config.models import ModuleThresholds
from humansays.const import (
    BROAD_EXCEPTION_NAMES,
    CLASS_VAR_NAMES,
    CLUSTER_MINIMUM,
    NON_STRUCTURAL_PREFIXES,
)
from humansays.enums import SignalName
from humansays.factories import string_set_map
from humansays.findings.models import Finding, Incident, Location, Observation

from .models import (
    BodyFacts,
    ParsedModule,
    ScopeContext,
    SelfUsage,
    Signature,
)
from .syntax import (
    annotation_is_bool,
    assigned_names,
    classify_boundary,
    contains_raise,
    dotted_name,
    referenced_names,
    resolve_alias,
    root_name,
)

FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)


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


def argument_defaults(node: ast.AST) -> dict[str, ast.AST]:
    positional = [*node.args.posonlyargs, *node.args.args]
    defaults: dict[str, ast.AST] = {}
    offset = len(node.args.defaults)
    paired = zip(positional[len(positional) - offset :], node.args.defaults, strict=True)
    for argument, default in paired:
        defaults[argument.arg] = default
    for argument, default in zip(
        node.args.kwonlyargs, node.args.kw_defaults, strict=True
    ):
        if default is not None:
            defaults[argument.arg] = default
    return defaults


def declared_arguments(node: ast.AST) -> list[ast.arg]:
    arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
    if node.args.vararg:
        arguments.append(node.args.vararg)
    if node.args.kwarg:
        arguments.append(node.args.kwarg)
    return arguments


def build_signature(node: ast.AST) -> Signature:
    arguments = declared_arguments(node)
    defaults = argument_defaults(node)
    boolean = []
    for argument in arguments:
        default = defaults.get(argument.arg)
        typed_bool = annotation_is_bool(argument.annotation)
        default_bool = isinstance(default, ast.Constant) and isinstance(
            default.value, bool
        )
        if typed_bool or default_bool:
            boolean.append(argument.arg)
    return Signature(
        parameters=tuple(argument.arg for argument in arguments),
        boolean_parameters=tuple(boolean),
    )


def is_trivial_accessor(node: ast.AST) -> bool:
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
    module: ParsedModule,
    thresholds: ModuleThresholds,
) -> list[Finding]:
    """HS017: an oversized file has usually stopped being one subject."""
    count = len(module.lines)
    if count <= thresholds.max_lines:
        return []
    location = Location('<module>', 1, max(1, count))
    observation = Observation(
        f'Module spans {count} source lines.',
        (f'configured threshold: {thresholds.max_lines}',),
    )
    return [build_finding(SignalName.HS017, location, observation)]


class FunctionVisitor(ast.NodeVisitor):
    def __init__(self, parameters: Iterable[str], context: ScopeContext) -> None:
        self.parameters = set(parameters)
        self.context = context.with_local_aliases()
        self.depth = 0
        self.body = BodyFacts()
        self.usage = SelfUsage()
        self.validated = string_set_map()

    # ast.NodeVisitor dispatch needs this exact signature; nested defs must not recurse
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: ARG002
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: ARG002
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: ARG002
        return

    def visit_Lambda(self, node: ast.Lambda) -> None:  # noqa: ARG002
        return

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name) and node.value.id == 'self':
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                self.usage.fields_written.add(node.attr)
            else:
                self.usage.fields_read.add(node.attr)
        name = dotted_name(node)
        if name:
            self._record_boundary(name, node.lineno)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for name in node.names:
            self.context.aliases[name.asname or name.name.split('.', 1)[0]] = name.name
        self._record_lazy_import(node, sorted(name.name for name in node.names))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            for name in node.names:
                self.context.aliases[name.asname or name.name] = (
                    f'{node.module}.{name.name}'
                )
        self._record_lazy_import(node, [node.module or '.'])

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._record_target(target, node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._record_target(node.target, node.lineno)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._record_target(node.target, node.lineno)
        self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        for target in node.targets:
            self._record_target(target, node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        call_name = dotted_name(node.func)
        if isinstance(node.func, ast.Attribute):
            self._record_call_target(node, call_name)
        if call_name:
            self._record_boundary(call_name, node.lineno)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        exception = dotted_name(node.type)
        if node.type is None:
            self._record_incident(SignalName.HS005, node.lineno, 'bare except')
        elif exception in BROAD_EXCEPTION_NAMES:
            disposition = 'broad exception'
            if not node.body or all(isinstance(item, ast.Pass) for item in node.body):
                disposition += ' silently ignored'
            self._record_incident(SignalName.HS005, node.lineno, disposition)
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.body.branches += 1
        if contains_raise(node.body):
            self._record_guard(node)
        self.visit(node.test)
        self._visit_nested(node.body)
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            self.visit(node.orelse[0])
        else:
            self._visit_nested(node.orelse)

    def visit_Assert(self, node: ast.Assert) -> None:
        for parameter in referenced_names(node.test) & self.parameters:
            self.validated[parameter].add(f'line {node.lineno}: assertion')
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.visit(node.target)
        self.visit(node.iter)
        self._visit_nested([*node.body, *node.orelse])

    visit_AsyncFor = visit_For  # noqa: N815 -- ast.NodeVisitor dispatch name

    def visit_While(self, node: ast.While) -> None:
        self.visit(node.test)
        self._visit_nested([*node.body, *node.orelse])

    def visit_Try(self, node: ast.Try) -> None:
        self._visit_nested(
            [*node.body, *node.handlers, *node.orelse, *node.finalbody],
        )

    visit_TryStar = visit_Try  # noqa: N815 -- ast.NodeVisitor dispatch name

    def visit_With(self, node: ast.With) -> None:
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars:
                self.visit(item.optional_vars)
        self._visit_nested(node.body)

    visit_AsyncWith = visit_With  # noqa: N815 -- ast.NodeVisitor dispatch name

    def visit_Match(self, node: ast.Match) -> None:
        self.visit(node.subject)
        for case in node.cases:
            self._visit_nested([case])

    def _record_incident(self, signal: SignalName, line: int, detail: str) -> None:
        self.body.incidents[signal].append(Incident(line, detail))

    def _record_lazy_import(self, node: ast.AST, modules: list[str]) -> None:
        self._record_incident(SignalName.HS021, node.lineno, ', '.join(modules))

    def _record_guard(self, node: ast.If) -> None:
        for parameter in referenced_names(node.test) & self.parameters:
            self.validated[parameter].add(
                f'line {node.lineno}: conditional guard raises',
            )

    def _record_call_target(self, node: ast.Call, call_name: str | None) -> None:
        attribute = node.func
        if root_name(attribute) == 'self':
            self.usage.methods_called.add(attribute.attr)
        if attribute.attr not in self.context.vocabulary.methods:
            return
        owner = self._owner(attribute.value)
        if owner:
            label = call_name or attribute.attr
            self.body.mutations[owner].add(f'line {node.lineno}: {label}(...)')

    def _visit_nested(self, nodes: Iterable[ast.AST]) -> None:
        self.depth += 1
        self.body.maximum_nesting = max(self.body.maximum_nesting, self.depth)
        for node in nodes:
            self.visit(node)
        self.depth -= 1

    def _record_target(self, target: ast.AST, line: int) -> None:
        owner = self._owner(target)
        if owner:
            self.body.mutations[owner].add(f'line {line}: assignment or deletion')

    def _owner(self, node: ast.AST) -> str | None:
        root = root_name(node)
        if root == 'self':
            return 'self'
        if root in self.parameters or root in self.context.module_globals:
            return root
        return None

    def _record_boundary(self, name: str, line: int) -> None:
        resolved = resolve_alias(name, self.context.aliases)
        boundary = classify_boundary(resolved)
        if boundary:
            self.body.boundaries[boundary].add(f'line {line}: {resolved}')
