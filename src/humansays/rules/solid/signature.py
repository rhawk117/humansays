"""HS002: a boolean parameter that selects behavior rather than carrying data."""

from humansays.config.models import Thresholds
from humansays.enums import SignalName
from humansays.facts.values import FunctionFacts
from humansays.rules.models import Emission


def boolean_modes(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    del thresholds
    booleans = facts.signature.operation_booleans
    setter = (
        facts.name.startswith('set_') and len(facts.signature.operation_parameters) == 1
    )
    if not booleans or setter:
        return []

    return [Emission(SignalName.HS002, facts.location, booleans)]
