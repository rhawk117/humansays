"""HS018, HS015, HS012, HS013 and HS016: the shape a class or module declares."""

from collections.abc import Iterable

from humansays.catalog import build_finding
from humansays.config.models import ClassThresholds
from humansays.const import CLUSTER_MINIMUM, NON_STRUCTURAL_PREFIXES
from humansays.enums import SignalName
from humansays.factories import string_set_map
from humansays.facts.module import ClassFacts
from humansays.facts.values import FunctionFacts, LambdaFact
from humansays.findings.models import Finding, Location, Observation


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


def base_classes(item: ClassFacts, thresholds: ClassThresholds) -> list[Finding]:
    """HS018: multiple parents make the method resolution order the real design."""
    bases = item.base_classes
    if len(bases) <= thresholds.max_base_classes:
        return []

    return [
        build_finding(
            SignalName.HS018,
            item.location,
            Observation(f'Class inherits from {len(bases)} parent classes.', bases),
        ),
    ]


def static_method(facts: FunctionFacts) -> list[Finding]:
    """HS015: a staticmethod is a module function wearing a class as a namespace."""
    if not facts.static_method:
        return []

    return [
        build_finding(
            SignalName.HS015,
            facts.location,
            Observation(
                'Method is declared @staticmethod, so it can reach neither instance '
                'nor class state.',
                (f'line {facts.location.line}: @staticmethod {facts.name}',),
            ),
        ),
    ]


def class_state_surface(item: ClassFacts, thresholds: ClassThresholds) -> list[Finding]:
    attributes = item.state_attributes
    if len(attributes) <= thresholds.max_attributes:
        return []

    findings = [
        build_finding(
            SignalName.HS012,
            item.location,
            Observation(
                f'Class owns {len(attributes)} state attributes.',
                tuple(sorted(attributes)),
            ),
        ),
    ]
    clusters = attribute_prefix_clusters(attributes)
    if clusters:
        evidence = tuple(
            f'{prefix}_*: {", ".join(names)}'
            for prefix, names in sorted(clusters.items())
        )
        findings.append(
            build_finding(
                SignalName.HS013,
                item.location,
                Observation(
                    f'Large class contains {len(clusters)} repeated '
                    'attribute-prefix clusters.',
                    evidence,
                ),
            ),
        )

    return findings


def lambda_signals(lambdas: tuple[LambdaFact, ...]) -> list[Finding]:
    """HS016: lambdas are anonymous, unimportable, and awkward to test."""
    return [
        build_finding(
            SignalName.HS016,
            Location(site.symbol, site.line, site.line),
            Observation(
                'Lambda expression stands in for a named function.',
                (f'line {site.line}: {site.source}',),
            ),
        )
        for site in lambdas
    ]
