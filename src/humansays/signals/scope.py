"""HS017 and HS004: module scale, and mutable state bound to a shared scope."""

from humansays.config.models import ModuleThresholds
from humansays.enums import SignalName
from humansays.facts.values import MutableBinding
from humansays.findings.models import Location
from humansays.rules.models import Emission


def module_scale(count: int, thresholds: ModuleThresholds) -> list[Emission]:
    if count <= thresholds.max_lines:
        return []

    return [
        Emission(
            SignalName.HS017,
            Location('<module>', 1, max(1, count)),
            (f'configured threshold: {thresholds.max_lines}',),
            payload={'count': count},
        ),
    ]


def mutable_bindings(
    bindings: tuple[MutableBinding, ...],
    symbol: str,
    scope: str,
) -> list[Emission]:
    return [
        Emission(
            SignalName.HS004,
            Location(symbol, binding.line, binding.end_line),
            (f'{binding.name} initialized as {binding.constructor}',),
            payload={'scope': scope, 'name': binding.name},
        )
        for binding in bindings
    ]
