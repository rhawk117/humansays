"""HS004 and HS006: state whose owner and lifetime are not obvious."""

from humansays.config.models import Thresholds
from humansays.const import MUTATION_OWNER_MINIMUM
from humansays.enums import SignalName
from humansays.facts.module import ClassFacts, ModuleFacts
from humansays.facts.values import FunctionFacts, MutableBinding
from humansays.findings.models import Location
from humansays.rules.models import Emission


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


def mutation_owners(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    del thresholds
    mutations = facts.body.mutations
    if len(mutations) < MUTATION_OWNER_MINIMUM:
        return []

    evidence = tuple(
        f'{owner}: {min(details)}' for owner, details in sorted(mutations.items())
    )
    return [
        Emission(
            SignalName.HS006,
            facts.location,
            evidence,
            payload={'count': len(mutations)},
        ),
    ]
