"""What a rule adapter is, and what it declares.

Signatures are uniform within a scope and deliberately not unified across
scopes. A per-class adapter and a per-function adapter consume different facts,
and collapsing them into one ``evaluate(facts)`` would put a dispatch back in
the middle of the walk.

An adapter is registered as a ``RuleAdapter`` record rather than as a bare
function carrying attributes. The record keeps the name and the declared rule
ids at the registration site, where the ordering they take part in is also
written down, and it gives the completeness tests something to key on.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from humansays.config.models import Thresholds
from humansays.enums import SignalName
from humansays.facts.module import ClassFacts, ModuleFacts
from humansays.facts.values import FunctionFacts
from humansays.rules.models import Emission

FactsT = TypeVar('FactsT', ModuleFacts, ClassFacts, FunctionFacts)


@dataclass(frozen=True, slots=True)
class RuleAdapter(Generic[FactsT]):
    name: str
    rule_ids: frozenset[SignalName]
    emit: Callable[[FactsT, Thresholds], list[Emission]]


ModuleAdapter = RuleAdapter[ModuleFacts]
ClassAdapter = RuleAdapter[ClassFacts]
FunctionAdapter = RuleAdapter[FunctionFacts]


def adapter(
    name: str,
    emit: Callable[[FactsT, Thresholds], list[Emission]],
    *rule_ids: SignalName,
) -> RuleAdapter[FactsT]:
    return RuleAdapter(name, frozenset(rule_ids), emit)
