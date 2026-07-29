"""The models that carry an ast node and therefore cannot leave this package."""

import ast
from dataclasses import dataclass, field
from pathlib import Path

from humansays.factories import mutable_constructors, mutating_methods

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
