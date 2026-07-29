"""HS008: whether a class's methods touch one field cluster or several."""

from humansays.catalog import build_finding
from humansays.const import COHESION_FIELD_MINIMUM, COHESION_METHOD_MINIMUM
from humansays.enums import SignalName
from humansays.facts.module import ClassFacts
from humansays.facts.values import FunctionFacts
from humansays.findings.models import Finding, Observation


def field_usage(method: FunctionFacts, method_names: frozenset[str]) -> frozenset[str]:
    non_fields = method_names | method.self_usage.methods_called
    fields = method.self_usage.fields_read | method.self_usage.fields_written
    return fields - non_fields


def cohesion_candidates(
    methods: tuple[FunctionFacts, ...],
) -> list[tuple[FunctionFacts, frozenset[str]]]:
    method_names = frozenset(method.name for method in methods)
    candidates = (
        (method, field_usage(method, method_names))
        for method in methods
        if not method.trivial_accessor and method.name != '__init__'
    )
    return [(method, fields) for method, fields in candidates if fields]


def connected_components(usage: list[frozenset[str]]) -> list[list[int]]:
    remaining = set(range(len(usage)))
    components: list[list[int]] = []
    while remaining:
        component = {remaining.pop()}
        additions = {0}
        while additions:
            shared: set[str] = set().union(*(usage[index] for index in component))
            additions = {index for index in remaining if shared & usage[index]}
            component |= additions
            remaining -= additions

        components.append(sorted(component))

    return components


def class_cohesion(item: ClassFacts) -> list[Finding]:
    eligible = cohesion_candidates(item.methods)
    usage = [fields for _, fields in eligible]
    fields = {name for group in usage for name in group}
    if len(eligible) < COHESION_METHOD_MINIMUM or len(fields) < COHESION_FIELD_MINIMUM:
        return []

    components = connected_components(usage)
    if len(components) < 2:
        return []

    evidence = []
    for component in components:
        names = [eligible[index][0].name for index in component]
        used = sorted(set().union(*(usage[index] for index in component)))
        evidence.append(f'methods {names} use fields {used}')

    return [
        build_finding(
            SignalName.HS008,
            item.location,
            Observation(
                f'Class methods form {len(components)} disconnected '
                'field-access clusters.',
                tuple(evidence),
            ),
        ),
    ]
