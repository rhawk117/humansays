"""Whole-module facts: the single value the evaluation layer receives."""

from dataclasses import dataclass
from pathlib import Path

from humansays.facts.values import FunctionFacts, LambdaFact, MutableBinding
from humansays.findings.models import Location


@dataclass(frozen=True, slots=True)
class ClassFacts:
    location: Location
    base_classes: tuple[str, ...]
    declared_attributes: frozenset[str]
    bindings: tuple[MutableBinding, ...]
    methods: tuple[FunctionFacts, ...]

    @property
    def name(self) -> str:
        return self.location.symbol

    @property
    def state_attributes(self) -> frozenset[str]:
        return self.declared_attributes | frozenset(
            attribute
            for method in self.methods
            for attribute in method.self_usage.fields_written
        )


@dataclass(frozen=True, slots=True)
class ModuleFacts:
    path: Path
    line_count: int
    bindings: tuple[MutableBinding, ...] = ()
    functions: tuple[FunctionFacts, ...] = ()
    classes: tuple[ClassFacts, ...] = ()
    lambdas: tuple[LambdaFact, ...] = ()

    @property
    def all_functions(self) -> tuple[FunctionFacts, ...]:
        methods = tuple(method for item in self.classes for method in item.methods)
        return self.functions + methods

    @property
    def symbols(self) -> tuple[str, ...]:
        names = {'<module>'}
        names.update(item.name for item in self.classes)
        names.update(item.location.symbol for item in self.all_functions)
        return tuple(sorted(names))
