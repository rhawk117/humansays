"""HS001, HS002 and HS014: what a signature asks its callers to supply."""

from humansays.config.models import Thresholds
from humansays.enums import SignalName
from humansays.facts.values import FunctionFacts
from humansays.rules.models import Emission


def argument_signals(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    signature = facts.signature
    operation = signature.operation_parameters
    emissions: list[Emission] = []
    if len(operation) > thresholds.functions.max_arguments:
        emissions.append(
            Emission(
                SignalName.HS001,
                facts.location,
                operation,
                payload={'count': len(operation)},
            ),
        )
        emissions.extend(validated_bundle(facts))

    booleans = signature.operation_booleans
    setter = facts.name.startswith('set_') and len(operation) == 1
    if booleans and not setter:
        emissions.append(Emission(SignalName.HS002, facts.location, booleans))

    return emissions


def validated_bundle(facts: FunctionFacts) -> list[Emission]:
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
        Emission(
            SignalName.HS014,
            facts.location,
            evidence,
            payload={'count': len(names)},
        ),
    ]
