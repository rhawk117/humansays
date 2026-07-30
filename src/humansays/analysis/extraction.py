"""The one place that walks a module and turns it into facts.

This is also the normalization boundary: interpreter differences stop here, and
`humansays.facts` and `humansays.rules` never learn which version parsed the
file. `tests/integration/test_analysis_confinement.py` is the enforcer.

No cache exists. When one is built, its key must include the interpreter
version, because facts extracted under one minor version are not valid under
another once the parser changes shape -- `ast.Str` and `ast.Num` were removed in
3.12, `type_params` was added to `FunctionDef`/`AsyncFunctionDef`/`ClassDef`,
`ast.TypeAlias` was added, and PEP 701 changed `JoinedStr` structure and column
offsets, which `analysis/syntax.py` reads for spans.
"""

import ast

from humansays.analysis.models import (
    FunctionTarget,
    MutationVocabulary,
    ParsedModule,
    ScopeContext,
)
from humansays.analysis.python_ast import (
    FUNCTION_NODES,
    base_class_names,
    build_function_facts,
    collect_aliases,
    collect_module_globals,
    declared_class_attributes,
    lambda_nodes,
    mutable_bindings,
)
from humansays.analysis.scopes import ScopeIndex
from humansays.analysis.syntax import location_of, node_span, snippet
from humansays.facts.module import ClassFacts, ModuleFacts
from humansays.facts.values import (
    FunctionFacts,
    LambdaFact,
    MutableBinding,
    Scope,
)


class ModuleExtractor:
    def __init__(
        self,
        module: ParsedModule,
        vocabulary: MutationVocabulary = MutationVocabulary(),  # noqa: B008 -- frozen, safe to share
    ) -> None:
        self.module = module
        self.context = ScopeContext(
            aliases=collect_aliases(module.tree),
            module_globals=collect_module_globals(module.tree),
            vocabulary=vocabulary,
        )
        self.scopes = ScopeIndex()

    def extract(self) -> ModuleFacts:
        tree = self.module.tree
        line_count = len(self.module.lines)
        self.scopes.add(Scope('<module>', 1, max(1, line_count)))

        functions: list[FunctionFacts] = []
        classes: list[ClassFacts] = []
        for node in tree.body:
            if isinstance(node, FUNCTION_NODES):
                functions.append(self._function(node, node.name))

            elif isinstance(node, ast.ClassDef):
                classes.append(self._class(node))

        return ModuleFacts(
            path=self.module.path,
            line_count=line_count,
            bindings=self._bindings(tree.body),
            functions=tuple(functions),
            classes=tuple(classes),
            lambdas=self._lambdas(tree),
        )

    def _class(self, node: ast.ClassDef) -> ClassFacts:
        self.scopes.add(Scope(node.name, *node_span(node)))
        methods = tuple(
            self._function(child, f'{node.name}.{child.name}', node.name)
            for child in node.body
            if isinstance(child, FUNCTION_NODES)
        )
        return ClassFacts(
            location=location_of(node.name, node),
            base_classes=base_class_names(node),
            declared_attributes=frozenset(declared_class_attributes(node)),
            bindings=self._bindings(node.body),
            methods=methods,
        )

    def _function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        qualified_name: str,
        class_name: str | None = None,
    ) -> FunctionFacts:
        target = FunctionTarget(node, qualified_name, class_name)
        facts = build_function_facts(self.module, target, self.context)
        self.scopes.add(
            Scope(qualified_name, facts.location.line, facts.location.end_line),
        )
        return facts

    def _bindings(self, body: list[ast.stmt]) -> tuple[MutableBinding, ...]:
        return tuple(
            mutable_bindings(
                body,
                self.context.aliases,
                self.context.vocabulary.constructors,
            ),
        )

    def _lambdas(self, tree: ast.Module) -> tuple[LambdaFact, ...]:
        return tuple(
            LambdaFact(
                line=node.lineno,
                source=snippet(node),
                symbol=self.scopes.for_line(node.lineno).symbol,
            )
            for node in lambda_nodes(tree)
        )


def extract(
    module: ParsedModule,
    vocabulary: MutationVocabulary = MutationVocabulary(),  # noqa: B008 -- frozen, safe to share
) -> ModuleFacts:
    return ModuleExtractor(module, vocabulary).extract()
