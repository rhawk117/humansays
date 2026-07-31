"""HS015: a staticmethod is a module function wearing a class as a namespace."""

from humansays.config.models import Thresholds
from humansays.enums import SignalName
from humansays.facts.values import FunctionFacts
from humansays.rules.models import Emission


def static_method(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    del thresholds
    if not facts.static_method:
        return []

    return [
        Emission(
            SignalName.HS015,
            facts.location,
            (f'line {facts.location.line}: @staticmethod {facts.name}',),
        ),
    ]
