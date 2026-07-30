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
from humansays.signals.scope import (
    class_shared_state,
    module_scale,
    module_shared_state,
)
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
        *argument_signals(facts, thresholds),
        *size_signals(facts, thresholds),
        *control_flow_signals(facts, thresholds),
        *incident_signals(facts, thresholds),
        *state_signals(facts, thresholds),
    ]


def class_signals(item: ClassFacts, thresholds: Thresholds) -> list[Emission]:
    emissions = [
        *class_shared_state(item, thresholds),
        *base_classes(item, thresholds),
    ]
    for method in item.methods:
        emissions.extend(function_signals(method, thresholds))
        emissions.extend(static_method(method, thresholds))

    emissions.extend(class_state_surface(item, thresholds))
    emissions.extend(class_cohesion(item, thresholds))
    return emissions


def evaluate(facts: ModuleFacts, thresholds: Thresholds) -> list[Finding]:
    emissions = [
        *module_scale(facts, thresholds),
        *module_shared_state(facts, thresholds),
    ]
    for item in facts.functions:
        emissions.extend(function_signals(item, thresholds))

    for item in facts.classes:
        emissions.extend(class_signals(item, thresholds))

    emissions.extend(lambda_signals(facts, thresholds))
    findings = [build_finding(emission) for emission in emissions]
    return sorted(findings, key=attrgetter('sort_key'))
