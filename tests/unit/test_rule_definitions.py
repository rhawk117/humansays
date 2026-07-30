"""Rule definitions loaded from ``rules.toml`` package data.

``test_specs_match_frozen_metadata`` is what keeps the definitions honest now
that they are the only source. The golden byte diff only covers rules that
actually fire on the corpus, so a rule that fires nowhere could have its
severity, confidence, weight or review question quietly changed and no other
test would notice. ``review_question`` is the most exposed of the four: it
reaches the JSON report only, so the text snapshot cannot see it either.

FROZEN was copied out of ``catalog.py`` while both sources existed and
``test_toml_matches_catalog`` proved them equal. Changing a value here is a
deliberate act; C1 changed none of them.
"""

import ast
import dataclasses
from pathlib import Path

import pytest

from humansays.enums import Disposition, Severity, SignalName
from humansays.rules.loading import (
    GROUPS,
    RuleDefinitionError,
    build_definition,
    collect_definitions,
    merge_groups,
    placeholders,
    read_group,
    rule_definitions,
)
from humansays.rules.models import RuleDefinition

VALID_ENTRY = {
    'id': 'HS017',
    'severity': 'warning',
    'confidence': 0.60,
    'weight': 3.0,
    'message': 'Module spans {count} source lines.',
    'review_question': 'Does this file hold one subject?',
    'disposition': 'on',
}


ORACLE = Path(__file__).resolve().parents[1] / 'golden/poc-parity/corpus/poc/catalog.py'

W = Severity.WARNING
A = Severity.ADVISORY

FROZEN = {
    'HS001': (W, 0.80, 3.0, 'Do these values form a request object, reusable configuration, or multiple responsibilities?'),
    'HS002': (A, 0.82, 1.0, 'Would keyword-only arguments, an enum, or separate operations communicate the modes better?'),
    'HS003': (W, 0.76, 3.0, 'Would guard clauses, a state model, or one meaningful extraction clarify the control flow?'),
    'HS004': (W, 0.95, 3.0, 'Is the lifetime intentional, who owns mutation, and can tests isolate this state?'),
    'HS005': (W, 0.96, 3.0, 'Which exceptions are expected, and should unexpected failures propagate?'),
    'HS006': (W, 0.70, 3.0, 'Are mutation authority, transaction boundaries, and partial-failure behavior clear?'),
    'HS007': (W, 0.65, 3.0, 'Should one function coordinate this many standard-library boundary categories directly?'),
    'HS008': (A, 0.65, 1.0, 'Do these clusters represent independently changing responsibilities that should have separate owners?'),
    'HS009': (A, 0.55, 1.0, 'Is the function cohesive, or does it mix workflow, decisions, and lower-level mechanics?'),
    'HS012': (A, 0.72, 1.0, 'Do subsets of this state have separate invariants, lifetimes, or reasons to change?'),
    'HS013': (W, 0.84, 3.0, 'Does each prefix identify a cohesive value object or component hidden inside this class?'),
    'HS014': (W, 0.88, 3.0, 'Should these arguments and their validation become one request, value, or configuration object?'),
    'HS015': (W, 0.99, 3.0, 'The method can reach neither instance nor class state, so what does class scope buy over a module-level function?'),
    'HS016': (W, 0.99, 3.0, 'What would this expression be named, and would a named function make it testable and reusable?'),
    'HS017': (W, 0.60, 3.0, 'Does this file hold one subject, or have several modules been accumulated into one namespace?'),
    'HS018': (W, 0.78, 3.0, 'Is this composition, mixin layering, or an inheritance chain that hides the real collaborators?'),
    'HS019': (W, 0.74, 3.0, 'Do these conditionals encode one decision that belongs in a table, mapping, or polymorphic dispatch?'),
    'HS021': (A, 0.85, 1.0, 'Is this hiding a cycle, an optional dependency, or a startup cost that belongs at module scope?'),
    'HS022': (W, 0.72, 3.0, 'How many distinct steps are in here, and which of them has a name already?'),
}  # fmt: skip


def entry_with(**changes: object) -> dict[str, object]:
    return VALID_ENTRY | changes


def oracle_review_questions() -> dict[str, str]:
    """Review questions from the vendored prototype catalog.

    The corpus under ``tests/golden/poc-parity`` is a frozen independent
    implementation, keyed ``PY0NN`` against the same rule numbers. It is not
    generated from anything humansays ships, so agreement is real evidence
    rather than a restatement.
    """
    tree = ast.parse(ORACLE.read_text(encoding='utf-8'))
    questions: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or getattr(node.func, 'id', '') != 'RuleSpec':
            continue

        keywords = {keyword.arg: keyword.value for keyword in node.keywords}
        signal = keywords['signal'].attr
        questions[f'HS{signal[2:]}'] = ast.literal_eval(keywords['review_question'])

    return questions


# Disposition is frozen separately from the other four fields, so demoting a
# rule is a one-line diff in a table that exists for nothing else. C2 sets every
# shipped rule to ON; the three the reconciliation maps to `hint` change here
# and nowhere else.
FROZEN_DISPOSITIONS = dict.fromkeys(FROZEN, Disposition.ON) | {
    # Demoted in phase C2, per docs/site/planned/reconciliation.md:21-41, which
    # maps all three to `hint`: emitted and shown, never weighed.
    'HS015': Disposition.HINT,
    'HS016': Disposition.HINT,
    'HS021': Disposition.HINT,
}


def test_specs_match_frozen_metadata() -> None:
    loaded = rule_definitions()
    assert {signal.name for signal in loaded} == set(FROZEN)
    for signal, definition in loaded.items():
        severity, confidence, weight, question = FROZEN[signal.name]
        assert dataclasses.asdict(definition.spec) == {
            'signal': signal,
            'severity': severity,
            'confidence': confidence,
            'weight': weight,
            'review_question': question,
            'disposition': FROZEN_DISPOSITIONS[signal.name],
        }, f'{signal.name} diverges from its frozen metadata'


def test_every_frozen_disposition_is_covered() -> None:
    """The disposition table must not go thin as rules are added or demoted."""
    assert set(FROZEN_DISPOSITIONS) == {signal.name for signal in rule_definitions()}


def test_review_questions_match_poc_oracle() -> None:
    oracle = oracle_review_questions()
    loaded = rule_definitions()
    # The prototype also carries PY010, PY011 and PY020, which humansays
    # deleted; only the shipped rules have to agree.
    assert {signal.name for signal in loaded}.issubset(oracle)
    divergent = {
        signal.name
        for signal, definition in loaded.items()
        if definition.spec.review_question != oracle[signal.name]
    }
    assert not divergent, f'review questions diverge from the prototype: {divergent}'


def test_every_signal_has_a_definition() -> None:
    assert set(rule_definitions()) == set(SignalName)


def test_no_signal_is_defined_in_two_groups() -> None:
    seen: dict[SignalName, str] = {}
    for group in GROUPS:
        for signal in read_group(group):
            assert signal not in seen, (
                f'{signal.name} is defined in both {seen[signal]} and {group}'
            )
            seen[signal] = group


def test_group_files_cover_every_group() -> None:
    counted = sum(len(read_group(group)) for group in GROUPS)
    assert counted == len(SignalName)


def test_collect_definitions_rejects_a_repeated_id() -> None:
    with pytest.raises(RuleDefinitionError, match='HS017 defined twice'):
        collect_definitions([VALID_ENTRY, VALID_ENTRY], 'kiss')


def test_merge_groups_rejects_a_signal_owned_by_two_groups() -> None:
    one = collect_definitions([VALID_ENTRY], 'kiss')
    with pytest.raises(RuleDefinitionError, match='HS017 is defined in both'):
        merge_groups({'kiss': one, 'smell': one})


def test_merge_groups_rejects_an_incomplete_catalog() -> None:
    with pytest.raises(RuleDefinitionError, match='no rule definition for'):
        merge_groups({'kiss': collect_definitions([VALID_ENTRY], 'kiss')})


def test_definitions_are_cached() -> None:
    assert rule_definitions() is rule_definitions()


def test_build_definition_accepts_a_well_formed_entry() -> None:
    definition = build_definition(VALID_ENTRY, 'kiss')
    assert isinstance(definition, RuleDefinition)
    assert definition.spec.signal is SignalName.HS017
    assert definition.placeholders == frozenset({'count'})


@pytest.mark.parametrize(
    ('entry', 'expected'),
    [
        (entry_with(threshold=80), 'unknown keys'),
        (entry_with(when='always'), 'unknown keys'),
        ({k: v for k, v in VALID_ENTRY.items() if k != 'weight'}, 'missing keys'),
        (entry_with(id='HS999'), 'not a SignalName member'),
        (entry_with(id=17), 'id must be a string'),
        (entry_with(severity='error'), 'unknown severity'),
        (entry_with(disposition='maybe'), 'unknown disposition'),
        (entry_with(disposition='ON'), 'unknown disposition'),
        (entry_with(disposition=1), 'disposition must be a string'),
        (
            {k: v for k, v in VALID_ENTRY.items() if k != 'disposition'},
            'missing keys',
        ),
        (entry_with(confidence=1.5), 'confidence out of range'),
        (entry_with(weight=-1.0), 'weight out of range'),
        (entry_with(confidence='high'), 'confidence must be a number'),
        (entry_with(confidence=True), 'confidence must be a number'),
        (entry_with(review_question=3), 'review_question must be a string'),
        (entry_with(message=['a']), 'message must be a string'),
    ],
)
def test_build_definition_rejects_malformed_entries(
    entry: dict[str, object],
    expected: str,
) -> None:
    with pytest.raises(RuleDefinitionError, match=expected):
        build_definition(entry, 'kiss')


@pytest.mark.parametrize(
    ('template', 'expected'),
    [
        ('Spans {0} lines.', 'plain name'),
        ('Spans {} lines.', 'plain name'),
        ('Spans {facts.length} lines.', 'plain name'),
        ('Spans {values[0]} lines.', 'plain name'),
        ('Spans {count!r} lines.', 'conversion'),
        ('Spans {count:>3} lines.', 'format spec'),
    ],
)
def test_placeholders_reject_anything_but_a_plain_name(
    template: str,
    expected: str,
) -> None:
    with pytest.raises(RuleDefinitionError, match=expected):
        placeholders(template, 'kiss/rules.toml: HS017')


def test_placeholders_of_a_static_message_are_empty() -> None:
    assert placeholders('Nothing to fill.', 'err/rules.toml: HS005') == frozenset()


def test_render_fills_every_placeholder() -> None:
    definition = build_definition(VALID_ENTRY, 'kiss')
    assert definition.render({'count': 412}) == 'Module spans 412 source lines.'


@pytest.mark.parametrize('payload', [{}, {'count': 1, 'extra': 2}, {'lines': 1}])
def test_render_rejects_a_payload_that_does_not_match(payload: dict) -> None:
    definition = build_definition(VALID_ENTRY, 'kiss')
    with pytest.raises(ValueError, match='do not match placeholders'):
        definition.render(payload)
