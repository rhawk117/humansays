"""HS005, HS021, HS006 and HS007: what a function body reaches for."""

from humansays.config.models import Thresholds
from humansays.const import BOUNDARY_MINIMUM, MUTATION_OWNER_MINIMUM
from humansays.enums import SignalName
from humansays.facts.values import FunctionFacts
from humansays.rules.models import Emission


def incident_signals(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    del thresholds
    return [
        Emission(
            signal,
            facts.location,
            (f'line {incident.line}: {incident.detail}',),
        )
        for signal, incidents in facts.body.incidents.items()
        for incident in incidents
    ]


def state_signals(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    del thresholds
    emissions: list[Emission] = []
    mutations = facts.body.mutations
    if len(mutations) >= MUTATION_OWNER_MINIMUM:
        evidence = tuple(
            f'{owner}: {min(details)}' for owner, details in sorted(mutations.items())
        )
        emissions.append(
            Emission(
                SignalName.HS006,
                facts.location,
                evidence,
                payload={'count': len(mutations)},
            ),
        )

    boundaries = facts.body.boundaries
    if len(boundaries) >= BOUNDARY_MINIMUM:
        evidence = tuple(
            f'{boundary}: {min(details)}'
            for boundary, details in sorted(boundaries.items())
        )
        emissions.append(
            Emission(
                SignalName.HS007,
                facts.location,
                evidence,
                payload={'count': len(boundaries)},
            ),
        )

    return emissions
