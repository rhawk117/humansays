"""Data models.

Pydantic models carry anything that can come from a config file or the command
line, so bad values fail at load time with a real error message. Plain
dataclasses carry the per-node facts built while walking a tree, where
validation would cost more than it buys.
"""

import ast
from dataclasses import dataclass, field
from operator import attrgetter
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .const import DEFAULT_EXCLUDES, IMPLICIT_PARAMETERS
from .enums import FailOn, Grade, OutputFormat, Severity, SignalName
from .factories import incident_map, mutable_constructors, mutating_methods, string_set_map


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class FunctionThresholds(Frozen):
    max_arguments: int = Field(default=3, ge=0)
    max_nesting: int = Field(default=3, ge=0)
    class_nesting_bonus: int = Field(default=1, ge=0)
    max_branches: int = Field(default=5, ge=0)
    max_lines: int = Field(default=50, ge=1)
    max_code_lines: int = Field(default=65, ge=1)

    def nesting_limit(self, class_name: str | None = None) -> int:
        if class_name is None:
            return self.max_nesting
        return self.max_nesting + self.class_nesting_bonus


class ClassThresholds(Frozen):
    max_attributes: int = Field(default=6, ge=0)
    max_base_classes: int = Field(default=1, ge=0)


class ModuleThresholds(Frozen):
    max_lines: int = Field(default=500, ge=1)


class Thresholds(Frozen):
    functions: FunctionThresholds = FunctionThresholds()
    classes: ClassThresholds = ClassThresholds()
    modules: ModuleThresholds = ModuleThresholds()


class Selection(Frozen):
    paths: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    symbol: str | None = None

    @property
    def excludes(self) -> frozenset[str]:
        return DEFAULT_EXCLUDES | frozenset(self.exclude)


class Report(Frozen):
    format: OutputFormat = OutputFormat.TEXT
    limit: int = Field(default=200, ge=0)
    fail_on: FailOn = FailOn.NEVER
    min_score: float = Field(default=0.0, ge=0.0, le=100.0)


class RuleSpec(Frozen):
    signal: SignalName
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    weight: float = Field(ge=0.0)
    review_question: str

    @property
    def rule_id(self) -> str:
        return self.signal.name

    @property
    def penalty(self) -> float:
        return self.weight * self.confidence


class Score(Frozen):
    lines: int
    penalty: float
    density: float
    value: float
    grade: Grade


@dataclass(frozen=True, slots=True)
class Location:
    symbol: str
    line: int
    end_line: int


@dataclass(frozen=True, slots=True)
class Observation:
    message: str
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Incident:
    line: int
    detail: str


@dataclass(frozen=True, slots=True)
class Finding:
    rule: RuleSpec
    location: Location
    observation: Observation

    @property
    def sort_key(self) -> tuple[int, str]:
        return (self.location.line, self.rule.rule_id)


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

    def with_local_aliases(self) -> "ScopeContext":
        return ScopeContext(dict(self.aliases), self.module_globals, self.vocabulary)


@dataclass(frozen=True, slots=True)
class Signature:
    parameters: tuple[str, ...] = ()
    boolean_parameters: tuple[str, ...] = ()
    validated_parameters: dict[str, set[str]] = field(default_factory=dict)

    @property
    def operation_parameters(self) -> tuple[str, ...]:
        return tuple(
            name for name in self.parameters if name not in IMPLICIT_PARAMETERS
        )

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
        return self.location.symbol.rsplit(".", 1)[-1]

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
        return min(candidates, key=attrgetter("span"))


@dataclass(frozen=True, slots=True)
class FileReport:
    path: Path
    lines: int
    classes: int
    functions: int
    symbols: set[str]
    findings: list[Finding]


@dataclass(frozen=True, slots=True)
class ScanResult:
    label: str
    reports: list[FileReport]
    errors: list[str]

    @property
    def findings(self) -> list[Finding]:
        return [finding for report in self.reports for finding in report.findings]

    @property
    def lines(self) -> int:
        return sum(report.lines for report in self.reports)
