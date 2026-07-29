"""Constraints on the fact model that make per-file caching plumbing later.

No cache is implemented. These assert the properties a cache would need:
facts hold no tree, they serialize, and one file's facts never reach
another's.
"""

from __future__ import annotations

import ast
import dataclasses
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from humansays.analysis.extraction import extract
from humansays.analysis.models import ParsedModule
from tests.fixtures import sources

if TYPE_CHECKING:
    from humansays.facts.module import ModuleFacts


def facts_for(source: str, name: str = '<snippet>') -> ModuleFacts:
    return extract(ParsedModule(Path(name), source, ast.parse(source)))


def walk(value: Any, seen: set[int] | None = None) -> list[Any]:
    seen = set() if seen is None else seen
    if id(value) in seen:
        return []

    seen.add(id(value))
    reached = [value]
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        for item in dataclasses.fields(value):
            reached.extend(walk(getattr(value, item.name), seen))

    elif isinstance(value, Mapping):
        for key, item in value.items():
            reached.extend(walk(key, seen))
            reached.extend(walk(item, seen))

    elif isinstance(value, (list, tuple, set, frozenset)) or (
        isinstance(value, Sequence) and not isinstance(value, (str, bytes))
    ):
        for item in value:
            reached.extend(walk(item, seen))

    return reached


def fact_objects(facts: Any) -> set[int]:
    return {
        id(value)
        for value in walk(facts)
        if dataclasses.is_dataclass(value) and not isinstance(value, type)
    }


def encodable(value: Any) -> Any:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            item.name: encodable(getattr(value, item.name))
            for item in dataclasses.fields(value)
        }

    if isinstance(value, Mapping):
        return {str(key): encodable(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set, frozenset)):
        return [encodable(item) for item in value]

    if isinstance(value, Path):
        return str(value)

    return value


class TestNoTreeReachableFromFacts:
    def test_no_ast_node_is_reachable_from_module_facts(self) -> None:
        facts = facts_for(sources.SMELLY_MODULE)
        offenders = [
            type(value).__name__ for value in walk(facts) if isinstance(value, ast.AST)
        ]
        assert offenders == []

    def test_the_walk_would_find_a_node_if_one_were_there(self) -> None:
        tree = ast.parse('x = 1')
        assert [value for value in walk({'tree': tree}) if isinstance(value, ast.AST)]


class TestFactsRejectMutation:
    def test_rebinding_a_field_raises(self) -> None:
        facts = facts_for(sources.DISCONNECTED_CLASS).classes[0].methods[0]
        for target, name in (
            (facts, 'trivial_accessor'),
            (facts.body, 'branches'),
            (facts.self_usage, 'fields_read'),
            (facts.signature, 'parameters'),
        ):
            with pytest.raises(dataclasses.FrozenInstanceError):
                setattr(target, name, None)

    def test_evidence_mappings_reject_assignment(self) -> None:
        facts = facts_for(sources.MULTIPLE_BOUNDARIES).functions[0]
        with pytest.raises(TypeError):
            facts.body.boundaries['network'] = ()

    def test_self_usage_sets_cannot_be_widened_in_place(self) -> None:
        facts = facts_for(sources.DISCONNECTED_CLASS).classes[0].methods[1]
        assert not hasattr(facts.self_usage.fields_read, 'add')


class TestFactsAreData:
    def test_module_facts_round_trip_through_json(self) -> None:
        facts = facts_for(sources.SMELLY_MODULE)
        payload = encodable(facts)
        restored = json.loads(json.dumps(payload, sort_keys=True))
        assert restored == json.loads(json.dumps(payload, sort_keys=True))
        assert restored['path'] == '<snippet>'
        assert restored['line_count'] == facts.line_count

    def test_extraction_is_deterministic(self) -> None:
        first = encodable(facts_for(sources.SMELLY_MODULE))
        second = encodable(facts_for(sources.SMELLY_MODULE))
        assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


class TestFactsAreSelfContained:
    def test_one_modules_facts_reach_nothing_from_another(self) -> None:
        first = facts_for(sources.SMELLY_MODULE, 'first.py')
        second = facts_for(sources.LAMBDAS_IN_THREE_SCOPES, 'second.py')
        assert not fact_objects(first) & fact_objects(second)

    def test_re_extracting_one_module_shares_no_fact_object(self) -> None:
        first = facts_for(sources.SMELLY_MODULE, 'same.py')
        second = facts_for(sources.SMELLY_MODULE, 'same.py')
        assert not fact_objects(first) & fact_objects(second)
