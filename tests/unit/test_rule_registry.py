"""The registry: what runs, in what order, and whether it covers every rule.

The relation between adapters and rules is many-to-many in two places, so it
is bounded by explicit allowlists rather than asserted as a bijection. Growing
the relation is then a deliberate edit to a named constant with a reason
attached, not drift that nothing notices.
"""

from __future__ import annotations

import ast
import random
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from humansays.analysis.extraction import extract
from humansays.analysis.models import ParsedModule
from humansays.config.models import Thresholds
from humansays.enums import SignalName
from humansays.rules import evaluate
from humansays.rules.loading import GROUPS, rule_definitions
from humansays.rules.registry import (
    ADAPTER_GROUPS,
    CLASS_HEAD_ADAPTERS,
    CLASS_TAIL_ADAPTERS,
    FUNCTION_ADAPTERS,
    METHOD_ADAPTERS,
    MODULE_ADAPTERS,
    MODULE_TAIL_ADAPTERS,
    build_finding,
)
from tests.fixtures import sources

if TYPE_CHECKING:
    from humansays.facts.module import ModuleFacts

REGISTRY = Path('src/humansays/rules/registry.py')
CORPUS = Path(__file__).resolve().parents[1] / 'golden/poc-parity/corpus'

# HS004 is the only rule two adapters declare: module-scope bindings and
# class-body bindings are different facts, so one callable cannot produce both.
MULTI_ADAPTER_RULES = frozenset({SignalName.HS004})

# Adapters that declare more than one rule, and why the pair is inseparable.
MULTI_RULE_ADAPTERS = {
    # HS014 is emitted inside HS001's branch.
    'contract.argument_contract': frozenset({SignalName.HS001, SignalName.HS014}),
    # HS013 is emitted inside HS012's branch.
    'solid.class_state_surface': frozenset({SignalName.HS012, SignalName.HS013}),
    # Two independent size checks over the same function facts.
    'kiss.function_scale': frozenset({SignalName.HS009, SignalName.HS022}),
    # Two independent control-flow checks over the same function facts.
    'kiss.control_flow': frozenset({SignalName.HS003, SignalName.HS019}),
}

ALL_ADAPTERS = [entry for group in ADAPTER_GROUPS for entry in group]

# Every scope walked, in the order evaluate() walks it.
WALK_FIXTURE = '''
"""Exercises module scope, a module function, a class with a method, and a lambda."""
REGISTRY = {}
PICK = lambda item: item


def render(payload):
    return payload


class Holder:
    CACHE = {}

    def pick(self, key):
        return self.CACHE[key]

    @staticmethod
    def classify(name):
        return name
'''


def analyze(source: str) -> list:
    module = ParsedModule(Path('<snippet>'), source, ast.parse(source))
    return evaluate(extract(module), Thresholds())


def corpus_facts() -> list:
    collected = []
    for path in sorted(CORPUS.rglob('*.py')):
        text = path.read_text(encoding='utf-8')
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue

        collected.append((path, extract(ParsedModule(path, text, tree))))

    return collected


def test_definitions_and_registry_agree() -> None:
    declared = {signal for entry in ALL_ADAPTERS for signal in entry.rule_ids}
    assert declared == set(rule_definitions()) == set(SignalName)


def test_multi_adapter_rules_are_allowlisted() -> None:
    counted = Counter(signal for entry in ALL_ADAPTERS for signal in entry.rule_ids)
    shared = {signal for signal, count in counted.items() if count > 1}
    assert shared == MULTI_ADAPTER_RULES


def test_multi_rule_adapters_are_allowlisted() -> None:
    bundled = {
        entry.name: entry.rule_ids for entry in ALL_ADAPTERS if len(entry.rule_ids) > 1
    }
    assert bundled == MULTI_RULE_ADAPTERS


def test_no_adapter_declares_a_rule_from_another_group() -> None:
    definitions_by_group = {
        group: {signal.name for signal in read}
        for group, read in _definitions_by_group().items()
    }
    misfiled = {
        (entry.name, signal.name)
        for entry in ALL_ADAPTERS
        for signal in entry.rule_ids
        if signal.name not in definitions_by_group[entry.name.split('.')[0]]
    }
    assert not misfiled, f'adapters declaring a rule from elsewhere: {sorted(misfiled)}'


def _definitions_by_group() -> dict:
    from humansays.rules.loading import read_group

    return {group: read_group(group) for group in GROUPS}


def test_adapter_names_are_unique() -> None:
    names = [entry.name for entry in ALL_ADAPTERS]
    assert len(names) == len(set(names))


def test_registry_order_is_literal() -> None:
    """Each scope's order is written out, not derived from anything at runtime.

    A decorator scan or a `pkgutil` walk would make the order depend on import
    or filesystem order, which is invariant 4's whole concern.
    """
    text = REGISTRY.read_text(encoding='utf-8')
    tree = ast.parse(text)
    assigned = {
        target.id: node.value
        for node in tree.body
        if isinstance(node, ast.AnnAssign | ast.Assign)
        for target in ([node.target] if isinstance(node, ast.AnnAssign) else node.targets)
        if isinstance(target, ast.Name)
    }
    for name in (
        'MODULE_ADAPTERS',
        'MODULE_TAIL_ADAPTERS',
        'FUNCTION_ADAPTERS',
        'METHOD_ADAPTERS',
        'CLASS_HEAD_ADAPTERS',
        'CLASS_TAIL_ADAPTERS',
    ):
        assert isinstance(assigned[name], ast.Tuple), f'{name} is not a literal tuple'

    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert 'pkgutil' not in imported, 'the registry scans for adapters'
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert '__subclasses__' not in attributes, 'the registry discovers adapters'


def test_every_registered_adapter_group_is_reachable() -> None:
    reachable = (
        MODULE_ADAPTERS,
        MODULE_TAIL_ADAPTERS,
        FUNCTION_ADAPTERS,
        METHOD_ADAPTERS,
        CLASS_HEAD_ADAPTERS,
        CLASS_TAIL_ADAPTERS,
    )
    assert reachable == ADAPTER_GROUPS


def test_no_two_adapters_share_a_sort_key() -> None:
    """HS004's two registrations must never collide.

    Module-scope and class-body bindings occupy disjoint source lines, which is
    a property of Python's grammar rather than of the type system. Measure it
    rather than assert it: if two adapters ever produced the same
    ``(line, rule_id)``, their relative order would decide the output and the
    "adapter order is free" argument would stop holding.
    """
    owners = _surveyed_owners()
    collisions = {key: names for key, names in owners.items() if len(names) > 1}
    assert not collisions, f'two adapters share a sort key: {collisions}'


def test_the_sort_key_survey_reaches_every_adapter() -> None:
    """Names the failure that ``_surveyed_owners`` already refuses to hide.

    The survey went thin once: the corpus and the fixtures alone never fired
    ``encap.class_shared_state``, HS004's other registration and the exact
    collision the survey exists to rule out. It reported safety it had not
    checked, and it did so by passing.
    """
    _surveyed_owners()


def _surveyed_owners() -> dict[tuple[Path, int, str], set[str]]:
    """Observed owners, but only once every registration has actually emitted.

    A collision survey that silently skips a registration is worse than no
    survey: it answers the question it was asked without having looked. So
    incomplete coverage fails here, in the shared helper, rather than in a
    neighbouring test that a reader might assume is belt-and-braces.
    """
    owners = _observed_owners()
    observed = {name for names in owners.values() for name in names}
    unreached = sorted({entry.name for entry in ALL_ADAPTERS} - observed)
    assert not unreached, (
        f'these adapters never emitted, so the survey proved nothing about '
        f'them: {unreached}. Add a source to _survey_sources() that fires each.'
    )
    return owners


def _observed_owners() -> dict[tuple[Path, int, str], set[str]]:
    owners: dict[tuple[Path, int, str], set[str]] = {}
    for path, facts in corpus_facts():
        _collect_owners(owners, path, facts)

    for name, source in _survey_sources():
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        _collect_owners(
            owners, Path(name), extract(ParsedModule(Path(name), source, tree))
        )

    return owners


def _survey_sources() -> list[tuple[str, str]]:
    named = [
        (name, value)
        for name, value in vars(sources).items()
        if not name.startswith('_') and isinstance(value, str)
    ]
    return [
        *named,
        ('<walk>', WALK_FIXTURE),
        ('<long-module>', sources.line_padding(600)),
        ('<long-function>', sources.padded_function(30, 30)),
    ]


def _collect_owners(owners: dict, origin: Path, facts: ModuleFacts) -> None:
    thresholds = Thresholds()
    for scope_adapters, targets in _scoped_targets(facts):
        for entry in scope_adapters:
            for target in targets:
                for emission in entry.emit(target, thresholds):
                    key = (origin, emission.location.line, emission.signal.name)
                    owners.setdefault(key, set()).add(entry.name)


def _scoped_targets(facts: ModuleFacts) -> list:
    methods = [method for item in facts.classes for method in item.methods]
    return [
        (MODULE_ADAPTERS, [facts]),
        (MODULE_TAIL_ADAPTERS, [facts]),
        (FUNCTION_ADAPTERS, [*facts.functions, *methods]),
        (METHOD_ADAPTERS, methods),
        (CLASS_HEAD_ADAPTERS, list(facts.classes)),
        (CLASS_TAIL_ADAPTERS, list(facts.classes)),
    ]


def test_evaluation_is_deterministic_across_repeated_runs() -> None:
    first = [finding.sort_key for finding in analyze(sources.SMELLY_MODULE)]
    for _ in range(5):
        assert [finding.sort_key for finding in analyze(sources.SMELLY_MODULE)] == first


@pytest.mark.parametrize('seed', [0, 1, 2])
def test_adapter_order_within_a_scope_does_not_change_the_output(seed: int) -> None:
    """Permuting a scope's adapters must not move a single finding.

    The sort is stable on ``(line, rule_id)``, so permutation can only matter
    for findings sharing both -- and those come from one adapter's own loop,
    which a permutation does not touch.
    """
    module = ParsedModule(Path('<snippet>'), WALK_FIXTURE, ast.parse(WALK_FIXTURE))
    facts = extract(module)
    expected = [
        (finding.rule.rule_id, finding.location.symbol, finding.location.line)
        for finding in evaluate(facts, Thresholds())
    ]

    rng = random.Random(seed)  # noqa: S311
    shuffled: list = []
    for scope_adapters, targets in _scoped_targets(facts):
        order = list(scope_adapters)
        rng.shuffle(order)
        shuffled.extend(
            emission
            for entry in order
            for target in targets
            for emission in entry.emit(target, Thresholds())
        )

    findings = sorted(
        (build_finding(emission) for emission in shuffled),
        key=lambda finding: finding.sort_key,
    )
    assert [
        (finding.rule.rule_id, finding.location.symbol, finding.location.line)
        for finding in findings
    ] == expected


def test_walk_order_covers_every_scope() -> None:
    """The fixture reaches module, function, class, method and lambda scope."""
    fired = {finding.rule.rule_id for finding in analyze(WALK_FIXTURE)}
    assert {'HS004', 'HS015', 'HS016'} <= fired
