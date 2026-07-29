"""Models that carry an ast node, plus re-exports of the moved fact types."""

import ast
from dataclasses import dataclass, field
from operator import attrgetter
from pathlib import Path

from humansays.factories import mutable_constructors, mutating_methods
from humansays.facts.values import (
    BodyFacts,
    FunctionFacts,
    LambdaFact,
    MutableBinding,
    Scope,
    SelfUsage,
    Signature,
)

__all__ = (
    'AnalysisIndex',
    'BodyFacts',
    'FunctionFacts',
    'FunctionNode',
    'FunctionTarget',
    'LambdaFact',
    'MutableBinding',
    'MutationVocabulary',
    'ParsedModule',
    'Scope',
    'ScopeContext',
    'SelfUsage',
    'Signature',
)

FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef


@dataclass(frozen=True, slots=True)
class ParsedModule:
    path: Path
    source: str
    tree: ast.Module

    @property
    def lines(self) -> list[str]:
        return self.source.splitlines()


@dataclass(frozen=True, slots=True)
class FunctionTarget:
    """One function to extract facts from, and the names it is known by."""

    node: FunctionNode
    qualified_name: str
    class_name: str | None = None


@dataclass(frozen=True, slots=True)
class MutationVocabulary:
    constructors: frozenset[str] = field(default_factory=mutable_constructors)
    methods: frozenset[str] = field(default_factory=mutating_methods)


@dataclass(frozen=True, slots=True)
class ScopeContext:
    aliases: dict[str, str]
    module_globals: set[str]
    vocabulary: MutationVocabulary

    def with_local_aliases(self) -> 'ScopeContext':
        return ScopeContext(dict(self.aliases), self.module_globals, self.vocabulary)


@dataclass(slots=True)
class AnalysisIndex:
    symbols: set[str] = field(default_factory=set)
    scopes: list[Scope] = field(default_factory=list)
    functions: list[FunctionFacts] = field(default_factory=list)
    classes: dict[str, list[FunctionFacts]] = field(default_factory=dict)

    def add_scope(self, scope: Scope) -> None:
        self.scopes.append(scope)
        self.symbols.add(scope.symbol)

    def scope_for_line(self, line: int) -> Scope:
        candidates = [scope for scope in self.scopes if scope.contains(line)]
        if not candidates:
            return self.scopes[0]

        return min(candidates, key=attrgetter('span'))
