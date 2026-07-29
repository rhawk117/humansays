"""Facts about one function, and the small values that describe a definition.

``Scope`` is line-based on purpose. It used to carry the ast node it came
from, which nothing read and which would have blocked caching a scope.
"""

from dataclasses import dataclass, field

from humansays.const import IMPLICIT_PARAMETERS
from humansays.enums import SignalName
from humansays.factories import incident_map, string_set_map
from humansays.findings.models import Incident, Location


@dataclass(frozen=True, slots=True)
class Scope:
    symbol: str
    line: int
    end_line: int

    @property
    def span(self) -> int:
        return self.end_line - self.line

    def contains(self, line: int) -> bool:
        return self.line <= line <= self.end_line


@dataclass(frozen=True, slots=True)
class LambdaFact:
    """A lambda expression and where it sits."""

    line: int
    source: str


@dataclass(frozen=True, slots=True)
class MutableBinding:
    """An assignment whose value is a mutable literal or container call."""

    name: str
    line: int
    end_line: int
    constructor: str


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
