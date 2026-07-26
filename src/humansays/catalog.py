"""The rule catalog.

``RULES`` is keyed by :class:`SignalName`, so a rule id is never a loose string:
``RULES[SignalName.HS015]`` is the only way to reach a spec, and a typo is an
immediate ``KeyError`` rather than a silently missing finding.
"""

from types import MappingProxyType

from .enums import Severity, SignalName
from .findings.models import Finding, Location, Observation, RuleSpec

WARNING_WEIGHT = 3.0
ADVISORY_WEIGHT = 1.0
NOTICE_WEIGHT = 0.0

RULES = MappingProxyType({
    SignalName.HS001: RuleSpec(
        signal=SignalName.HS001,
        severity=Severity.WARNING,
        confidence=0.80,
        weight=WARNING_WEIGHT,
        review_question=(
            "Do these values form a request object, reusable configuration, "
            "or multiple responsibilities?"
        ),
    ),
    SignalName.HS002: RuleSpec(
        signal=SignalName.HS002,
        severity=Severity.ADVISORY,
        confidence=0.82,
        weight=ADVISORY_WEIGHT,
        review_question=(
            "Would keyword-only arguments, an enum, or separate operations "
            "communicate the modes better?"
        ),
    ),
    SignalName.HS003: RuleSpec(
        signal=SignalName.HS003,
        severity=Severity.WARNING,
        confidence=0.76,
        weight=WARNING_WEIGHT,
        review_question=(
            "Would guard clauses, a state model, or one meaningful extraction "
            "clarify the control flow?"
        ),
    ),
    SignalName.HS004: RuleSpec(
        signal=SignalName.HS004,
        severity=Severity.WARNING,
        confidence=0.95,
        weight=WARNING_WEIGHT,
        review_question=(
            "Is the lifetime intentional, who owns mutation, and can tests "
            "isolate this state?"
        ),
    ),
    SignalName.HS005: RuleSpec(
        signal=SignalName.HS005,
        severity=Severity.WARNING,
        confidence=0.96,
        weight=WARNING_WEIGHT,
        review_question=(
            "Which exceptions are expected, and should unexpected failures "
            "propagate?"
        ),
    ),
    SignalName.HS006: RuleSpec(
        signal=SignalName.HS006,
        severity=Severity.WARNING,
        confidence=0.70,
        weight=WARNING_WEIGHT,
        review_question=(
            "Are mutation authority, transaction boundaries, and "
            "partial-failure behavior clear?"
        ),
    ),
    SignalName.HS007: RuleSpec(
        signal=SignalName.HS007,
        severity=Severity.WARNING,
        confidence=0.65,
        weight=WARNING_WEIGHT,
        review_question=(
            "Should one function coordinate this many standard-library "
            "boundary categories directly?"
        ),
    ),
    SignalName.HS008: RuleSpec(
        signal=SignalName.HS008,
        severity=Severity.ADVISORY,
        confidence=0.65,
        weight=ADVISORY_WEIGHT,
        review_question=(
            "Do these clusters represent independently changing "
            "responsibilities that should have separate owners?"
        ),
    ),
    SignalName.HS009: RuleSpec(
        signal=SignalName.HS009,
        severity=Severity.ADVISORY,
        confidence=0.55,
        weight=ADVISORY_WEIGHT,
        review_question=(
            "Is the function cohesive, or does it mix workflow, decisions, "
            "and lower-level mechanics?"
        ),
    ),
    SignalName.HS012: RuleSpec(
        signal=SignalName.HS012,
        severity=Severity.ADVISORY,
        confidence=0.72,
        weight=ADVISORY_WEIGHT,
        review_question=(
            "Do subsets of this state have separate invariants, lifetimes, or "
            "reasons to change?"
        ),
    ),
    SignalName.HS013: RuleSpec(
        signal=SignalName.HS013,
        severity=Severity.WARNING,
        confidence=0.84,
        weight=WARNING_WEIGHT,
        review_question=(
            "Does each prefix identify a cohesive value object or component "
            "hidden inside this class?"
        ),
    ),
    SignalName.HS014: RuleSpec(
        signal=SignalName.HS014,
        severity=Severity.WARNING,
        confidence=0.88,
        weight=WARNING_WEIGHT,
        review_question=(
            "Should these arguments and their validation become one request, "
            "value, or configuration object?"
        ),
    ),
    SignalName.HS015: RuleSpec(
        signal=SignalName.HS015,
        severity=Severity.WARNING,
        confidence=0.99,
        weight=WARNING_WEIGHT,
        review_question=(
            "The method can reach neither instance nor class state, so what "
            "does class scope buy over a module-level function?"
        ),
    ),
    SignalName.HS016: RuleSpec(
        signal=SignalName.HS016,
        severity=Severity.WARNING,
        confidence=0.99,
        weight=WARNING_WEIGHT,
        review_question=(
            "What would this expression be named, and would a named function "
            "make it testable and reusable?"
        ),
    ),
    SignalName.HS017: RuleSpec(
        signal=SignalName.HS017,
        severity=Severity.WARNING,
        confidence=0.60,
        weight=WARNING_WEIGHT,
        review_question=(
            "Does this file hold one subject, or have several modules been "
            "accumulated into one namespace?"
        ),
    ),
    SignalName.HS018: RuleSpec(
        signal=SignalName.HS018,
        severity=Severity.WARNING,
        confidence=0.78,
        weight=WARNING_WEIGHT,
        review_question=(
            "Is this composition, mixin layering, or an inheritance chain "
            "that hides the real collaborators?"
        ),
    ),
    SignalName.HS019: RuleSpec(
        signal=SignalName.HS019,
        severity=Severity.WARNING,
        confidence=0.74,
        weight=WARNING_WEIGHT,
        review_question=(
            "Do these conditionals encode one decision that belongs in a "
            "table, mapping, or polymorphic dispatch?"
        ),
    ),
    SignalName.HS021: RuleSpec(
        signal=SignalName.HS021,
        severity=Severity.ADVISORY,
        confidence=0.85,
        weight=ADVISORY_WEIGHT,
        review_question=(
            "Is this hiding a cycle, an optional dependency, or a startup "
            "cost that belongs at module scope?"
        ),
    ),
    SignalName.HS022: RuleSpec(
        signal=SignalName.HS022,
        severity=Severity.WARNING,
        confidence=0.72,
        weight=WARNING_WEIGHT,
        review_question=(
            "How many distinct steps are in here, and which of them has a "
            "name already?"
        ),
    ),
})


def rule_for(signal: SignalName) -> RuleSpec:
    return RULES[signal]


def build_finding(
    signal: SignalName,
    location: Location,
    observation: Observation,
) -> Finding:
    return Finding(RULES[signal], location, observation)
