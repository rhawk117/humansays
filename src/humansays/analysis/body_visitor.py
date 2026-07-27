"""Walking one function body.

``python_ast`` describes what a definition declares; this module records what
its body does: how deeply it nests, what it branches on, what it mutates, what
it imports late, and which standard-library boundaries it touches.
"""

import ast
from collections.abc import Iterable

from humansays.const import BROAD_EXCEPTION_NAMES
from humansays.enums import SignalName
from humansays.factories import string_set_map
from humansays.findings.models import Incident

from .models import BodyFacts, ScopeContext, SelfUsage
from .syntax import (
    classify_boundary,
    contains_raise,
    dotted_name,
    referenced_names,
    resolve_alias,
    root_name,
)


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

    # ast.NodeVisitor dispatch name; For/AsyncFor share every field this visitor reads
    visit_AsyncFor = visit_For  # noqa: N815 # ty: ignore[invalid-method-override]

    def visit_While(self, node: ast.While) -> None:
        self.visit(node.test)
        self._visit_nested([*node.body, *node.orelse])

    def visit_Try(self, node: ast.Try) -> None:
        self._visit_nested(
            [*node.body, *node.handlers, *node.orelse, *node.finalbody],
        )

    # ast.NodeVisitor dispatch name; Try/TryStar share every field this visitor reads
    visit_TryStar = visit_Try  # noqa: N815 # ty: ignore[invalid-method-override]

    def visit_With(self, node: ast.With) -> None:
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars:
                self.visit(item.optional_vars)

        self._visit_nested(node.body)

    # ast.NodeVisitor dispatch name; With/AsyncWith share every field this visitor reads
    visit_AsyncWith = visit_With  # noqa: N815 # ty: ignore[invalid-method-override]

    def visit_Match(self, node: ast.Match) -> None:
        self.visit(node.subject)
        for case in node.cases:
            self._visit_nested([case])

    def _record_incident(self, signal: SignalName, line: int, detail: str) -> None:
        self.body.incidents[signal].append(Incident(line, detail))

    def _record_lazy_import(
        self,
        node: ast.Import | ast.ImportFrom,
        modules: list[str],
    ) -> None:
        self._record_incident(SignalName.HS021, node.lineno, ', '.join(modules))

    def _record_guard(self, node: ast.If) -> None:
        for parameter in referenced_names(node.test) & self.parameters:
            self.validated[parameter].add(
                f'line {node.lineno}: conditional guard raises',
            )

    def _record_call_target(self, node: ast.Call, call_name: str | None) -> None:
        attribute = node.func
        if not isinstance(attribute, ast.Attribute):
            return

        if root_name(attribute) == 'self':
            self.usage.methods_called.add(attribute.attr)

        if attribute.attr not in self.context.vocabulary.methods:
            return

        owner = self._owner(attribute.value)
        if not owner:
            return

        label = call_name or attribute.attr
        self.body.mutations[owner].add(f'line {node.lineno}: {label}(...)')

    def _visit_nested(self, nodes: Iterable[ast.AST]) -> None:
        self.depth += 1
        self.body.maximum_nesting = max(self.body.maximum_nesting, self.depth)
        for node in nodes:
            self.visit(node)

        self.depth -= 1

    def _record_target(self, target: ast.AST, line: int) -> None:
        if not (owner := self._owner(target)):
            return

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
        if not (boundary := classify_boundary(resolved)):
            return

        self.body.boundaries[boundary].add(f'line {line}: {resolved}')
