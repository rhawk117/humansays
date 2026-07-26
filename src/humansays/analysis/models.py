"""Per-node fact models.

Plain dataclasses carrying facts built while walking a tree, where validation
would cost more than it buys. This is the only model module that imports
``ast``: it holds the parse result and everything derived from it.
"""

import ast
from dataclasses import dataclass, field
from operator import attrgetter
from pathlib import Path

from humansays.const import IMPLICIT_PARAMETERS
from humansays.enums import SignalName
from humansays.factories import (
    incident_map,
    mutable_constructors,
    mutating_methods,
    string_set_map,
)
from humansays.findings.models import Incident, Location

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
class Scope:
    node: ast.AST
    symbol: str
    line: int
    end_line: int

    @property
    def span(self) -> int:
        return self.end_line - self.line

    def contains(self, line: int) -> bool:
        return self.line <= line <= self.end_line


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


@dataclass(frozen=True, slots=True)
class Signature:
    parameters: tuple[str, ...] = ()
    boolean_parameters: tuple[str, ...] = ()
    validated_parameters: dict[str, set[str]] = field(default_factory=dict)

    @property
    def operation_parameters(self) -> tuple[str, ...]:
        return tuple(name for name in self.parameters if name not in IMPLICIT_PARAMETERS)

    @property
    def operation_booleans(self) -> tuple[str, ...]:
        return tuple(
            name for name in self.boolean_parameters if name not in IMPLICIT_PARAMETERS
        )


@dataclass(slots=True)
class BodyFacts:
    maximum_nesting: int = 0
    branches: int = 0
    code_lines: int = 0
    mutations: dict[str, set[str]] = field(default_factory=string_set_map)
    boundaries: dict[str, set[str]] = field(default_factory=string_set_map)
    incidents: dict[SignalName, list[Incident]] = field(default_factory=incident_map)


@dataclass(slots=True)
class SelfUsage:
    fields_read: set[str] = field(default_factory=set)
    fields_written: set[str] = field(default_factory=set)
    methods_called: set[str] = field(default_factory=set)


@dataclass(slots=True)
class FunctionFacts:
    location: Location
    class_name: str | None
    signature: Signature
    body: BodyFacts
    self_usage: SelfUsage
    trivial_accessor: bool

    @property
    def name(self) -> str:
        return self.location.symbol.rsplit('.', 1)[-1]

    @property
    def length(self) -> int:
        return self.location.end_line - self.location.line + 1


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
