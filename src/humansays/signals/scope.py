"""HS017 and HS004: module scale, and mutable state bound to a shared scope."""

from humansays.config.models import Thresholds
from humansays.enums import SignalName
from humansays.facts.module import ClassFacts, ModuleFacts
from humansays.facts.values import MutableBinding
from humansays.findings.models import Location
from humansays.rules.models import Emission


def module_scale(facts: ModuleFacts, thresholds: Thresholds) -> list[Emission]:
    count = facts.line_count
    limit = thresholds.modules.max_lines
    if count <= limit:
        return []

    return [
        Emission(
            SignalName.HS017,
            Location('<module>', 1, max(1, count)),
            (f'configured threshold: {limit}',),
            payload={'count': count},
        ),
    ]


def shared_state(
    bindings: tuple[MutableBinding, ...],
    symbol: str,
    scope: str,
) -> list[Emission]:
    """HS004 for one scope's bindings.

    Module-scope and class-scope bindings need separate adapters, because one
    callable cannot consume both ``ModuleFacts`` and ``ClassFacts``. The
    detection stays here so the two adapters cannot drift apart.
    """
    return [
        Emission(
            SignalName.HS004,
            Location(symbol, binding.line, binding.end_line),
            (f'{binding.name} initialized as {binding.constructor}',),
            payload={'scope': scope, 'name': binding.name},
        )
        for binding in bindings
    ]


def module_shared_state(facts: ModuleFacts, thresholds: Thresholds) -> list[Emission]:
    del thresholds
    return shared_state(facts.bindings, '<module>', 'module')


def class_shared_state(item: ClassFacts, thresholds: Thresholds) -> list[Emission]:
    del thresholds
    return shared_state(item.bindings, item.name, 'class')
