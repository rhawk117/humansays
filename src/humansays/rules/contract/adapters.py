"""HS001 and HS014: what a signature asks its callers to supply.

HS014 is emitted inside HS001's branch rather than beside it: an argument
bundle is only worth naming once the bundle is already too wide, so the two
stay one adapter.
"""

from humansays.config.models import Thresholds
from humansays.enums import SignalName
from humansays.facts.values import FunctionFacts
from humansays.rules.models import Emission


def argument_contract(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    operation = facts.signature.operation_parameters
    if len(operation) <= thresholds.functions.max_arguments:
        return []

    return [
        Emission(
            SignalName.HS001,
            facts.location,
            operation,
            payload={'count': len(operation)},
        ),
        *validated_bundle(facts),
    ]


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
