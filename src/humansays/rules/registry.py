"""Which adapters run, in which order, at which scope, and what they produce.

Order is literal. No decorator scan, no ``pkgutil`` walk, no
``__subclasses__``: a tuple written out in one file is diffable, cannot depend
on import or filesystem order, and puts each adapter's declared rule ids next
to the position it occupies.

Adapter order *within* a scope instance is in fact free. ``evaluate`` sorts by
``(line, rule_id)`` with a stable sort, so two findings tie only when they
share both, which can only happen inside one adapter's own loop. The order that
is not free is the scope walk itself, which ``evaluation.py`` owns.
"""

from humansays.enums import SignalName
from humansays.findings.models import Finding, Observation
from humansays.rules.contract.adapters import argument_contract
from humansays.rules.encap.adapters import (
    class_shared_state,
    module_shared_state,
    mutation_owners,
)
from humansays.rules.err.adapters import broad_exception
from humansays.rules.idiom.adapters import lazy_import
from humansays.rules.kiss.adapters import control_flow, function_scale, module_scale
from humansays.rules.loading import rule_definitions
from humansays.rules.models import Emission
from humansays.rules.protocol import ClassAdapter, FunctionAdapter, ModuleAdapter, adapter
from humansays.rules.smell.adapters import lambda_signals
from humansays.rules.solid.class_shape import base_classes, class_state_surface
from humansays.rules.solid.cohesion import class_cohesion
from humansays.rules.solid.effects import boundary_categories
from humansays.rules.solid.signature import boolean_modes
from humansays.rules.yagni.adapters import static_method

MODULE_ADAPTERS: tuple[ModuleAdapter, ...] = (
    adapter('kiss.module_scale', module_scale, SignalName.HS017),
    adapter('encap.module_shared_state', module_shared_state, SignalName.HS004),
)

# Lambdas are collected at module scope but reported after every function and
# class, so they are a second module pass rather than part of the first.
MODULE_TAIL_ADAPTERS: tuple[ModuleAdapter, ...] = (
    adapter('smell.lambda_signals', lambda_signals, SignalName.HS016),
)

FUNCTION_ADAPTERS: tuple[FunctionAdapter, ...] = (
    adapter(
        'contract.argument_contract',
        argument_contract,
        SignalName.HS001,
        SignalName.HS014,
    ),
    adapter('solid.boolean_modes', boolean_modes, SignalName.HS002),
    adapter('kiss.function_scale', function_scale, SignalName.HS009, SignalName.HS022),
    adapter('kiss.control_flow', control_flow, SignalName.HS003, SignalName.HS019),
    adapter('err.broad_exception', broad_exception, SignalName.HS005),
    adapter('idiom.lazy_import', lazy_import, SignalName.HS021),
    adapter('encap.mutation_owners', mutation_owners, SignalName.HS006),
    adapter('solid.boundary_categories', boundary_categories, SignalName.HS007),
)

# Methods get every function adapter first, then the ones that only mean
# anything on a method.
METHOD_ADAPTERS: tuple[FunctionAdapter, ...] = (
    adapter('yagni.static_method', static_method, SignalName.HS015),
)

CLASS_HEAD_ADAPTERS: tuple[ClassAdapter, ...] = (
    adapter('encap.class_shared_state', class_shared_state, SignalName.HS004),
    adapter('solid.base_classes', base_classes, SignalName.HS018),
)

CLASS_TAIL_ADAPTERS: tuple[ClassAdapter, ...] = (
    adapter(
        'solid.class_state_surface',
        class_state_surface,
        SignalName.HS012,
        SignalName.HS013,
    ),
    adapter('solid.class_cohesion', class_cohesion, SignalName.HS008),
)

ADAPTER_GROUPS = (
    MODULE_ADAPTERS,
    MODULE_TAIL_ADAPTERS,
    FUNCTION_ADAPTERS,
    METHOD_ADAPTERS,
    CLASS_HEAD_ADAPTERS,
    CLASS_TAIL_ADAPTERS,
)


def build_finding(emission: Emission) -> Finding:
    """The single construction site: definition plus measurement.

    Rule metadata is reached through ``rule_definitions()``, which is keyed by
    :class:`SignalName`, so a rule id is never a loose string and a typo is an
    immediate ``KeyError`` rather than a silently missing finding.
    """
    definition = rule_definitions()[emission.signal]
    return Finding(
        definition.spec,
        emission.location,
        Observation(definition.render(emission.payload), emission.evidence),
    )
