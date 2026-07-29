"""HS001, HS002 and HS014: what a signature asks its callers to supply."""

from humansays.catalog import build_finding
from humansays.config.models import FunctionThresholds
from humansays.enums import SignalName
from humansays.facts.values import FunctionFacts
from humansays.findings.models import Finding, Observation


def argument_signals(
    facts: FunctionFacts,
    thresholds: FunctionThresholds,
) -> list[Finding]:
    signature = facts.signature
    operation = signature.operation_parameters
    findings: list[Finding] = []
    if len(operation) > thresholds.max_arguments:
        findings.append(
            build_finding(
                SignalName.HS001,
                facts.location,
                Observation(
                    f'Function accepts {len(operation)} operation arguments.',
                    operation,
                ),
            ),
        )
        findings.extend(validated_bundle(facts))

    booleans = signature.operation_booleans
    setter = facts.name.startswith('set_') and len(operation) == 1
    if booleans and not setter:
        findings.append(
            build_finding(
                SignalName.HS002,
                facts.location,
                Observation(
                    'Boolean parameters select behavior or operating modes.',
                    booleans,
                ),
            ),
        )

    return findings


def validated_bundle(facts: FunctionFacts) -> list[Finding]:
    validated = facts.signature.validated_parameters
    names = tuple(
        parameter
        for parameter in facts.signature.operation_parameters
        if parameter in validated
    )
    if not names:
        return []

    evidence = tuple(f'{parameter}: {min(validated[parameter])}' for parameter in names)
    return [
        build_finding(
            SignalName.HS014,
            facts.location,
            Observation(
                f'Function validates {len(names)} of its argument bundle internally.',
                evidence,
            ),
        ),
    ]
