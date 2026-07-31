"""HS007: how many standard-library boundary categories one function reaches."""

from humansays.config.models import Thresholds
from humansays.const import BOUNDARY_MINIMUM
from humansays.enums import SignalName
from humansays.facts.values import FunctionFacts
from humansays.rules.models import Emission


def boundary_categories(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    del thresholds
    boundaries = facts.body.boundaries
    if len(boundaries) < BOUNDARY_MINIMUM:
        return []

    evidence = tuple(
        f'{boundary}: {min(details)}' for boundary, details in sorted(boundaries.items())
    )
    return [
        Emission(
            SignalName.HS007,
            facts.location,
            evidence,
            payload={'count': len(boundaries)},
        ),
    ]
