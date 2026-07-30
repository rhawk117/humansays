"""Deleted-rule behavior: PY010 (comments), PY011 (docstring) and PY020
(future-annotations) no longer exist anywhere in humansays.
"""

import ast
from pathlib import Path

from humansays.analysis.extraction import extract
from humansays.analysis.models import ParsedModule
from humansays.config.models import Thresholds
from humansays.enums import SignalName
from humansays.rules.loading import rule_definitions
from humansays.signals import evaluate
from tests.fixtures import sources

DELETED_IDS = frozenset({'HS010', 'HS011', 'HS020'})


def analyze(source: str) -> list:
    module = ParsedModule(Path('<snippet>'), source, ast.parse(source))
    return evaluate(extract(module), Thresholds())


def test_deleted_ids_are_absent_from_signal_name() -> None:
    assert DELETED_IDS.isdisjoint(SignalName.__members__)


def test_deleted_ids_are_absent_from_the_definitions() -> None:
    defined = {signal.name for signal in rule_definitions()}
    assert DELETED_IDS.isdisjoint(defined)


def test_future_annotations_import_yields_no_finding() -> None:
    findings = analyze(sources.FUTURE_ANNOTATIONS)
    assert not any(finding.rule.rule_id == 'HS020' for finding in findings)
    assert not findings


def test_other_future_features_still_yield_no_finding() -> None:
    findings = analyze(sources.FUTURE_OTHER_FEATURE)
    assert not findings
