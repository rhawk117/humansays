"""Mutable scratch state for one function body, frozen into facts by ``freeze``."""

from dataclasses import dataclass, field
from types import MappingProxyType

from humansays.enums import SignalName
from humansays.factories import incident_map, string_set_map
from humansays.facts.values import BodyFacts, SelfUsage, frozen_evidence
from humansays.findings.models import Incident


@dataclass(slots=True)
class BodyAccumulator:
    maximum_nesting: int = 0
    branches: int = 0
    code_lines: int = 0
    mutations: dict[str, set[str]] = field(default_factory=string_set_map)
    boundaries: dict[str, set[str]] = field(default_factory=string_set_map)
    incidents: dict[SignalName, list[Incident]] = field(default_factory=incident_map)

    def freeze(self) -> BodyFacts:
        return BodyFacts(
            maximum_nesting=self.maximum_nesting,
            branches=self.branches,
            code_lines=self.code_lines,
            mutations=frozen_evidence(self.mutations),
            boundaries=frozen_evidence(self.boundaries),
            incidents=MappingProxyType({
                signal: tuple(items) for signal, items in self.incidents.items()
            }),
        )


@dataclass(slots=True)
class UsageAccumulator:
    fields_read: set[str] = field(default_factory=set)
    fields_written: set[str] = field(default_factory=set)
    methods_called: set[str] = field(default_factory=set)

    def freeze(self) -> SelfUsage:
        return SelfUsage(
            fields_read=frozenset(self.fields_read),
            fields_written=frozenset(self.fields_written),
            methods_called=frozenset(self.methods_called),
        )
