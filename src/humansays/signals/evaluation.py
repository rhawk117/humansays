"""The driver: walks facts in emission order and sorts what the rules return."""

from operator import attrgetter

from humansays.config.models import Thresholds
from humansays.facts.module import ClassFacts, ModuleFacts
from humansays.facts.values import FunctionFacts
from humansays.findings.models import Finding
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


def function_signals(facts: FunctionFacts, thresholds: Thresholds) -> list[Finding]:
    return [
        *argument_signals(facts, thresholds.functions),
        *size_signals(facts, thresholds.functions),
        *control_flow_signals(facts, thresholds.functions),
        *incident_signals(facts),
        *state_signals(facts),
    ]


def class_signals(item: ClassFacts, thresholds: Thresholds) -> list[Finding]:
    findings = [
        *mutable_bindings(item.bindings, item.name, 'class'),
        *base_classes(item, thresholds.classes),
    ]
    for method in item.methods:
        findings.extend(function_signals(method, thresholds))
        findings.extend(static_method(method))

    findings.extend(class_state_surface(item, thresholds.classes))
    findings.extend(class_cohesion(item))
    return findings


def evaluate(facts: ModuleFacts, thresholds: Thresholds) -> list[Finding]:
    findings = [
        *module_scale(facts.line_count, thresholds.modules),
        *mutable_bindings(facts.bindings, '<module>', 'module'),
    ]
    for item in facts.functions:
        findings.extend(function_signals(item, thresholds))

    for item in facts.classes:
        findings.extend(class_signals(item, thresholds))

    findings.extend(lambda_signals(facts.lambdas))
    return sorted(findings, key=attrgetter('sort_key'))
