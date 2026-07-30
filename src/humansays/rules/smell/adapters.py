"""HS016: lambdas are anonymous, unimportable, and awkward to test."""

from humansays.config.models import Thresholds
from humansays.enums import SignalName
from humansays.facts.module import ModuleFacts
from humansays.findings.models import Location
from humansays.rules.models import Emission


def lambda_signals(facts: ModuleFacts, thresholds: Thresholds) -> list[Emission]:
    del thresholds
    return [
        Emission(
            SignalName.HS016,
            Location(site.symbol, site.line, site.line),
            (f'line {site.line}: {site.source}',),
        )
        for site in facts.lambdas
    ]
