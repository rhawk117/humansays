"""HS005, HS021, HS006 and HS007: what a function body reaches for."""

from types import MappingProxyType

from humansays.catalog import build_finding
from humansays.const import BOUNDARY_MINIMUM, MUTATION_OWNER_MINIMUM
from humansays.enums import SignalName
from humansays.facts.values import FunctionFacts
from humansays.findings.models import Finding, Observation

INCIDENT_MESSAGES = MappingProxyType({
    SignalName.HS005: 'Broad exception handling may collapse unrelated failures.',
    SignalName.HS021: 'Import is deferred into the function body.',
})


def incident_signals(facts: FunctionFacts) -> list[Finding]:
    return [
        build_finding(
            signal,
            facts.location,
            Observation(
                INCIDENT_MESSAGES[signal],
                (f'line {incident.line}: {incident.detail}',),
            ),
        )
        for signal, incidents in facts.body.incidents.items()
        for incident in incidents
    ]


def state_signals(facts: FunctionFacts) -> list[Finding]:
    findings: list[Finding] = []
    mutations = facts.body.mutations
    if len(mutations) >= MUTATION_OWNER_MINIMUM:
        evidence = tuple(
            f'{owner}: {min(details)}' for owner, details in sorted(mutations.items())
        )
        findings.append(
            build_finding(
                SignalName.HS006,
                facts.location,
                Observation(
                    f'Function appears to mutate {len(mutations)} independent '
                    'state owners.',
                    evidence,
                ),
            ),
        )

    boundaries = facts.body.boundaries
    if len(boundaries) >= BOUNDARY_MINIMUM:
        evidence = tuple(
            f'{boundary}: {min(details)}'
            for boundary, details in sorted(boundaries.items())
        )
        findings.append(
            build_finding(
                SignalName.HS007,
                facts.location,
                Observation(
                    f'Function uses {len(boundaries)} standard-library boundary '
                    'categories.',
                    evidence,
                ),
            ),
        )

    return findings
