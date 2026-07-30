"""HS018, HS015, HS012, HS013 and HS016: the shape a class or module declares."""

from collections.abc import Iterable

from humansays.config.models import ClassThresholds
from humansays.const import CLUSTER_MINIMUM, NON_STRUCTURAL_PREFIXES
from humansays.enums import SignalName
from humansays.factories import string_set_map
from humansays.facts.module import ClassFacts
from humansays.facts.values import FunctionFacts, LambdaFact
from humansays.findings.models import Location
from humansays.rules.models import Emission


def attribute_prefix_clusters(attributes: Iterable[str]) -> dict[str, tuple[str, ...]]:
    grouped = string_set_map()
    for attribute in attributes:
        prefix, separator, _ = attribute.lstrip('_').partition('_')
        if separator and prefix not in NON_STRUCTURAL_PREFIXES:
            grouped[prefix].add(attribute)

    return {
        prefix: tuple(sorted(names))
        for prefix, names in grouped.items()
        if len(names) >= CLUSTER_MINIMUM
    }


def base_classes(item: ClassFacts, thresholds: ClassThresholds) -> list[Emission]:
    """HS018: multiple parents make the method resolution order the real design."""
    bases = item.base_classes
    if len(bases) <= thresholds.max_base_classes:
        return []

    return [
        Emission(SignalName.HS018, item.location, bases, payload={'count': len(bases)}),
    ]


def static_method(facts: FunctionFacts) -> list[Emission]:
    """HS015: a staticmethod is a module function wearing a class as a namespace."""
    if not facts.static_method:
        return []

    return [
        Emission(
            SignalName.HS015,
            facts.location,
            (f'line {facts.location.line}: @staticmethod {facts.name}',),
        ),
    ]


def class_state_surface(item: ClassFacts, thresholds: ClassThresholds) -> list[Emission]:
    attributes = item.state_attributes
    if len(attributes) <= thresholds.max_attributes:
        return []

    emissions = [
        Emission(
            SignalName.HS012,
            item.location,
            tuple(sorted(attributes)),
            payload={'count': len(attributes)},
        ),
    ]
    clusters = attribute_prefix_clusters(attributes)
    if clusters:
        evidence = tuple(
            f'{prefix}_*: {", ".join(names)}'
            for prefix, names in sorted(clusters.items())
        )
        emissions.append(
            Emission(
                SignalName.HS013,
                item.location,
                evidence,
                payload={'count': len(clusters)},
            ),
        )

    return emissions


def lambda_signals(lambdas: tuple[LambdaFact, ...]) -> list[Emission]:
    """HS016: lambdas are anonymous, unimportable, and awkward to test."""
    return [
        Emission(
            SignalName.HS016,
            Location(site.symbol, site.line, site.line),
            (f'line {site.line}: {site.source}',),
        )
        for site in lambdas
    ]
