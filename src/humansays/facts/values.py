"""Facts about one function, and the small values that describe a definition."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from humansays.const import IMPLICIT_PARAMETERS
from humansays.enums import SignalName
from humansays.findings.models import Incident, Location

EMPTY_EVIDENCE: Mapping[str, tuple[str, ...]] = MappingProxyType({})
EMPTY_INCIDENTS: Mapping[SignalName, tuple[Incident, ...]] = MappingProxyType({})


def frozen_evidence(groups: Mapping[str, Iterable[str]]) -> Mapping[str, tuple[str, ...]]:
    return MappingProxyType({
        key: tuple(sorted(values)) for key, values in groups.items()
    })


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
    """A lambda expression, where it sits, and the scope it resolves to."""

    line: int
    source: str
    symbol: str = '<module>'


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
    validated_parameters: Mapping[str, tuple[str, ...]] = EMPTY_EVIDENCE

    @property
    def operation_parameters(self) -> tuple[str, ...]:
        return tuple(name for name in self.parameters if name not in IMPLICIT_PARAMETERS)

    @property
    def operation_booleans(self) -> tuple[str, ...]:
        return tuple(
            name for name in self.boolean_parameters if name not in IMPLICIT_PARAMETERS
        )


@dataclass(frozen=True, slots=True)
class BodyFacts:
    maximum_nesting: int = 0
    branches: int = 0
    code_lines: int = 0
    mutations: Mapping[str, tuple[str, ...]] = EMPTY_EVIDENCE
    boundaries: Mapping[str, tuple[str, ...]] = EMPTY_EVIDENCE
    incidents: Mapping[SignalName, tuple[Incident, ...]] = EMPTY_INCIDENTS


@dataclass(frozen=True, slots=True)
class SelfUsage:
    fields_read: frozenset[str] = frozenset()
    fields_written: frozenset[str] = frozenset()
    methods_called: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class FunctionFacts:
    location: Location
    signature: Signature
    body: BodyFacts
    self_usage: SelfUsage
    trivial_accessor: bool
    static_method: bool = False

    @property
    def name(self) -> str:
        return self.location.symbol.rsplit('.', 1)[-1]

    @property
    def class_name(self) -> str | None:
        owner, separator, _ = self.location.symbol.rpartition('.')
        return owner if separator else None

    @property
    def length(self) -> int:
        return self.location.end_line - self.location.line + 1
