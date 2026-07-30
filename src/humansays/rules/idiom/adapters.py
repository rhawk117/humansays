"""HS021: an import moved into a function body."""

from humansays.config.models import Thresholds
from humansays.enums import SignalName
from humansays.facts.values import FunctionFacts
from humansays.rules.models import Emission


def lazy_import(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    del thresholds
    return [
        Emission(
            SignalName.HS021,
            facts.location,
            (f'line {incident.line}: {incident.detail}',),
        )
        for incident in facts.body.incidents.get(SignalName.HS021, ())
    ]
