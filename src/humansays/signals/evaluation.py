"""The driver: walks facts in emission order and sorts what the rules return."""

from operator import attrgetter

from humansays.catalog import build_finding
from humansays.config.models import Thresholds
from humansays.facts.module import ClassFacts, ModuleFacts
from humansays.facts.values import FunctionFacts
from humansays.findings.models import Finding
from humansays.rules.models import Emission
from humansays.signals.cohesion import class_cohesion
from humansays.signals.effects import incident_signals, state_signals
from humansays.signals.scope import module_scale, mutable_bindings
from humansays.signals.shape import control_flow_signals, size_signals
from humansays.signals.signature import argument_signals
from humansays.signals.structure import (
    base_classes,
    class_state_surface,
    lambda_signals,
    static_method,
)


def function_signals(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    return [
        *argument_signals(facts, thresholds.functions),
        *size_signals(facts, thresholds.functions),
        *control_flow_signals(facts, thresholds.functions),
        *incident_signals(facts),
        *state_signals(facts),
    ]


def class_signals(item: ClassFacts, thresholds: Thresholds) -> list[Emission]:
    emissions = [
        *mutable_bindings(item.bindings, item.name, 'class'),
        *base_classes(item, thresholds.classes),
    ]
    for method in item.methods:
        emissions.extend(function_signals(method, thresholds))
        emissions.extend(static_method(method))

    emissions.extend(class_state_surface(item, thresholds.classes))
    emissions.extend(class_cohesion(item))
    return emissions


def evaluate(facts: ModuleFacts, thresholds: Thresholds) -> list[Finding]:
    emissions = [
        *module_scale(facts.line_count, thresholds.modules),
        *mutable_bindings(facts.bindings, '<module>', 'module'),
    ]
    for item in facts.functions:
        emissions.extend(function_signals(item, thresholds))

    for item in facts.classes:
        emissions.extend(class_signals(item, thresholds))

    emissions.extend(lambda_signals(facts.lambdas))
    findings = [build_finding(emission) for emission in emissions]
    return sorted(findings, key=attrgetter('sort_key'))
