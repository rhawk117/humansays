"""HS017 and HS004: module scale, and mutable state bound to a shared scope."""

from humansays.catalog import build_finding
from humansays.config.models import ModuleThresholds
from humansays.enums import SignalName
from humansays.facts.values import MutableBinding
from humansays.findings.models import Finding, Location, Observation


def module_scale(count: int, thresholds: ModuleThresholds) -> list[Finding]:
    if count <= thresholds.max_lines:
        return []

    location = Location('<module>', 1, max(1, count))
    observation = Observation(
        f'Module spans {count} source lines.',
        (f'configured threshold: {thresholds.max_lines}',),
    )
    return [build_finding(SignalName.HS017, location, observation)]


def mutable_bindings(
    bindings: tuple[MutableBinding, ...],
    symbol: str,
    scope: str,
) -> list[Finding]:
    return [
        build_finding(
            SignalName.HS004,
            Location(symbol, binding.line, binding.end_line),
            Observation(
                f'Mutable {scope}-scope state `{binding.name}` is shared beyond '
                'one instance or operation.',
                (f'{binding.name} initialized as {binding.constructor}',),
            ),
        )
        for binding in bindings
    ]
