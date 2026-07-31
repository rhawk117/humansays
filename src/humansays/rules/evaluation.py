"""The driver: walks facts in emission order and sorts what the rules return.

The walk order is the part that has to be preserved exactly. Module work
before functions, functions before classes, lambdas last, a class's methods in
source order, and the class head and tail phases either side of the method
loop. Ties on ``(line, rule_id)`` do occur -- several incidents can share one
function location, and two lambdas can share a line -- and a stable sort
resolves them by input order.
"""

from operator import attrgetter

from humansays.config.models import Thresholds
from humansays.facts.module import ClassFacts, ModuleFacts
from humansays.facts.values import FunctionFacts
from humansays.findings.models import Finding
from humansays.rules.models import Emission
from humansays.rules.protocol import ClassAdapter, FunctionAdapter, ModuleAdapter
from humansays.rules.registry import (
    CLASS_HEAD_ADAPTERS,
    CLASS_TAIL_ADAPTERS,
    FUNCTION_ADAPTERS,
    METHOD_ADAPTERS,
    MODULE_ADAPTERS,
    MODULE_TAIL_ADAPTERS,
    build_finding,
    is_emitted,
)


def run_module(
    adapters: tuple[ModuleAdapter, ...],
    facts: ModuleFacts,
    thresholds: Thresholds,
) -> list[Emission]:
    return [item for entry in adapters for item in entry.emit(facts, thresholds)]


def run_class(
    adapters: tuple[ClassAdapter, ...],
    item: ClassFacts,
    thresholds: Thresholds,
) -> list[Emission]:
    return [found for entry in adapters for found in entry.emit(item, thresholds)]


def run_function(
    adapters: tuple[FunctionAdapter, ...],
    facts: FunctionFacts,
    thresholds: Thresholds,
) -> list[Emission]:
    return [item for entry in adapters for item in entry.emit(facts, thresholds)]


def function_signals(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    return run_function(FUNCTION_ADAPTERS, facts, thresholds)


def class_signals(item: ClassFacts, thresholds: Thresholds) -> list[Emission]:
    emissions = run_class(CLASS_HEAD_ADAPTERS, item, thresholds)
    for method in item.methods:
        emissions.extend(function_signals(method, thresholds))
        emissions.extend(run_function(METHOD_ADAPTERS, method, thresholds))

    emissions.extend(run_class(CLASS_TAIL_ADAPTERS, item, thresholds))
    return emissions


def evaluate(facts: ModuleFacts, thresholds: Thresholds) -> list[Finding]:
    emissions = run_module(MODULE_ADAPTERS, facts, thresholds)
    for item in facts.functions:
        emissions.extend(function_signals(item, thresholds))

    for item in facts.classes:
        emissions.extend(class_signals(item, thresholds))

    emissions.extend(run_module(MODULE_TAIL_ADAPTERS, facts, thresholds))
    findings = [build_finding(e) for e in emissions if is_emitted(e)]
    return sorted(findings, key=attrgetter('sort_key'))
