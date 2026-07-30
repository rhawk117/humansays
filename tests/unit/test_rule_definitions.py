"""Rule definitions loaded from ``rules.toml`` package data.

``test_toml_matches_catalog`` is the transcription proof: it holds while
``catalog.RULES`` is still the live table, so a mistyped confidence or a dropped
word in a review question fails here rather than surviving into the switchover.
It is replaced by a frozen-literal assertion once the catalog is gone.
"""

import dataclasses

import pytest

from humansays.catalog import RULES
from humansays.enums import SignalName
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
}


def entry_with(**changes: object) -> dict[str, object]:
    return VALID_ENTRY | changes


def test_toml_matches_catalog() -> None:
    loaded = rule_definitions()
    assert set(loaded) == set(RULES)
    for signal, spec in RULES.items():
        assert dataclasses.asdict(loaded[signal].spec) == dataclasses.asdict(spec), (
            f'{signal.name} definition diverges from the catalog'
        )


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
