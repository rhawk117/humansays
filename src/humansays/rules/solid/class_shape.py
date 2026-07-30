"""HS018, HS012 and HS013: the surface a class declares.

HS013 is emitted only inside the branch that emits HS012, and stays in the same
adapter. Splitting them would duplicate the attribute-count gate and the
clustering call, and no fixture would catch the drift if HS013 started firing
on a class HS012 did not.
"""

from collections.abc import Iterable

from humansays.config.models import Thresholds
from humansays.const import CLUSTER_MINIMUM, NON_STRUCTURAL_PREFIXES
from humansays.enums import SignalName
from humansays.factories import string_set_map
from humansays.facts.module import ClassFacts
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


def base_classes(item: ClassFacts, thresholds: Thresholds) -> list[Emission]:
    """HS018: multiple parents make the method resolution order the real design."""
    bases = item.base_classes
    if len(bases) <= thresholds.classes.max_base_classes:
        return []

    return [
        Emission(SignalName.HS018, item.location, bases, payload={'count': len(bases)}),
    ]


def class_state_surface(item: ClassFacts, thresholds: Thresholds) -> list[Emission]:
    attributes = item.state_attributes
    if len(attributes) <= thresholds.classes.max_attributes:
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
