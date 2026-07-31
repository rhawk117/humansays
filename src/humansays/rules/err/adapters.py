"""HS005: a handler broad enough to swallow failures it was not written for."""

from humansays.config.models import Thresholds
from humansays.enums import SignalName
from humansays.facts.values import FunctionFacts
from humansays.rules.models import Emission


def broad_exception(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    del thresholds
    return [
        Emission(
            SignalName.HS005,
            facts.location,
            (f'line {incident.line}: {incident.detail}',),
        )
        for incident in facts.body.incidents.get(SignalName.HS005, ())
    ]
