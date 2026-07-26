"""The rule catalog.

``RULES`` is keyed by :class:`SignalName`, so a rule id is never a loose string:
``RULES[SignalName.PY015]`` is the only way to reach a spec, and a typo is an
immediate ``KeyError`` rather than a silently missing finding.

``weight`` feeds the score. PY010 and PY011 are deliberately weightless — they
mark every comment and docstring for a reader's attention, so counting them as
damage would make the score a measure of how well documented the code is.
"""

from types import MappingProxyType

from .enums import Severity, SignalName
from .models import Finding, Location, Observation, RuleSpec

WARNING_WEIGHT = 3.0
ADVISORY_WEIGHT = 1.0
NOTICE_WEIGHT = 0.0

RULES = MappingProxyType({
    SignalName.PY001: RuleSpec(
        signal=SignalName.PY001,
        severity=Severity.WARNING,
        confidence=0.80,
        weight=WARNING_WEIGHT,
        review_question="Do these values form a request object, reusable configuration, or multiple responsibilities?",
    ),
    SignalName.PY002: RuleSpec(
        signal=SignalName.PY002,
        severity=Severity.ADVISORY,
        confidence=0.82,
        weight=ADVISORY_WEIGHT,
        review_question="Would keyword-only arguments, an enum, or separate operations communicate the modes better?",
    ),
    SignalName.PY003: RuleSpec(
        signal=SignalName.PY003,
        severity=Severity.WARNING,
        confidence=0.76,
        weight=WARNING_WEIGHT,
        review_question="Would guard clauses, a state model, or one meaningful extraction clarify the control flow?",
    ),
    SignalName.PY004: RuleSpec(
        signal=SignalName.PY004,
        severity=Severity.WARNING,
        confidence=0.95,
        weight=WARNING_WEIGHT,
        review_question="Is the lifetime intentional, who owns mutation, and can tests isolate this state?",
    ),
    SignalName.PY005: RuleSpec(
        signal=SignalName.PY005,
        severity=Severity.WARNING,
        confidence=0.96,
        weight=WARNING_WEIGHT,
        review_question="Which exceptions are expected, and should unexpected failures propagate?",
    ),
    SignalName.PY006: RuleSpec(
        signal=SignalName.PY006,
        severity=Severity.WARNING,
        confidence=0.70,
        weight=WARNING_WEIGHT,
        review_question="Are mutation authority, transaction boundaries, and partial-failure behavior clear?",
    ),
    SignalName.PY007: RuleSpec(
        signal=SignalName.PY007,
        severity=Severity.WARNING,
        confidence=0.65,
        weight=WARNING_WEIGHT,
        review_question="Should one function coordinate this many standard-library boundary categories directly?",
    ),
    SignalName.PY008: RuleSpec(
        signal=SignalName.PY008,
        severity=Severity.ADVISORY,
        confidence=0.65,
        weight=ADVISORY_WEIGHT,
        review_question="Do these clusters represent independently changing responsibilities that should have separate owners?",
    ),
    SignalName.PY009: RuleSpec(
        signal=SignalName.PY009,
        severity=Severity.ADVISORY,
        confidence=0.55,
        weight=ADVISORY_WEIGHT,
        review_question="Is the function cohesive, or does it mix workflow, decisions, and lower-level mechanics?",
    ),
    SignalName.PY010: RuleSpec(
        signal=SignalName.PY010,
        severity=Severity.ADVISORY,
        confidence=0.70,
        weight=NOTICE_WEIGHT,
        review_question="Do comments compensate for unclear code, preserve stale assumptions, or encode required constraints?",
    ),
    SignalName.PY011: RuleSpec(
        signal=SignalName.PY011,
        severity=Severity.ADVISORY,
        confidence=0.75,
        weight=NOTICE_WEIGHT,
        review_question="Does the docstring add durable contract information rather than restating the code?",
    ),
    SignalName.PY012: RuleSpec(
        signal=SignalName.PY012,
        severity=Severity.ADVISORY,
        confidence=0.72,
        weight=ADVISORY_WEIGHT,
        review_question="Do subsets of this state have separate invariants, lifetimes, or reasons to change?",
    ),
    SignalName.PY013: RuleSpec(
        signal=SignalName.PY013,
        severity=Severity.WARNING,
        confidence=0.84,
        weight=WARNING_WEIGHT,
        review_question="Does each prefix identify a cohesive value object or component hidden inside this class?",
    ),
    SignalName.PY014: RuleSpec(
        signal=SignalName.PY014,
        severity=Severity.WARNING,
        confidence=0.88,
        weight=WARNING_WEIGHT,
        review_question="Should these arguments and their validation become one request, value, or configuration object?",
    ),
    SignalName.PY015: RuleSpec(
        signal=SignalName.PY015,
        severity=Severity.WARNING,
        confidence=0.99,
        weight=WARNING_WEIGHT,
        review_question="The method can reach neither instance nor class state, so what does class scope buy over a module-level function?",
    ),
    SignalName.PY016: RuleSpec(
        signal=SignalName.PY016,
        severity=Severity.WARNING,
        confidence=0.99,
        weight=WARNING_WEIGHT,
        review_question="What would this expression be named, and would a named function make it testable and reusable?",
    ),
    SignalName.PY017: RuleSpec(
        signal=SignalName.PY017,
        severity=Severity.WARNING,
        confidence=0.60,
        weight=WARNING_WEIGHT,
        review_question="Does this file hold one subject, or have several modules been accumulated into one namespace?",
    ),
    SignalName.PY018: RuleSpec(
        signal=SignalName.PY018,
        severity=Severity.WARNING,
        confidence=0.78,
        weight=WARNING_WEIGHT,
        review_question="Is this composition, mixin layering, or an inheritance chain that hides the real collaborators?",
    ),
    SignalName.PY019: RuleSpec(
        signal=SignalName.PY019,
        severity=Severity.WARNING,
        confidence=0.74,
        weight=WARNING_WEIGHT,
        review_question="Do these conditionals encode one decision that belongs in a table, mapping, or polymorphic dispatch?",
    ),
    SignalName.PY020: RuleSpec(
        signal=SignalName.PY020,
        severity=Severity.WARNING,
        confidence=0.99,
        weight=WARNING_WEIGHT,
        review_question="Which annotations still need deferred evaluation on a supported runtime, and what breaks when they stay strings?",
    ),
    SignalName.PY021: RuleSpec(
        signal=SignalName.PY021,
        severity=Severity.ADVISORY,
        confidence=0.85,
        weight=ADVISORY_WEIGHT,
        review_question="Is this hiding a cycle, an optional dependency, or a startup cost that belongs at module scope?",
    ),
    SignalName.PY022: RuleSpec(
        signal=SignalName.PY022,
        severity=Severity.WARNING,
        confidence=0.72,
        weight=WARNING_WEIGHT,
        review_question="How many distinct steps are in here, and which of them has a name already?",
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
