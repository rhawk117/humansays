"""Deleted-rule behavior: PY010 (comments), PY011 (docstring), PY020
(future-annotations) no longer exist anywhere in humansays, and ast/tokenize
stay confined to humansays.analysis.
"""

import ast
from pathlib import Path

import poc_fixtures as fixtures

from humansays.analysis.models import ParsedModule
from humansays.analysis.rules import Analyzer
from humansays.catalog import RULES
from humansays.config.models import Thresholds
from humansays.enums import SignalName

SRC_ROOT = Path(__file__).resolve().parent.parent.parent / 'src' / 'humansays'
DELETED_IDS = frozenset({'HS010', 'HS011', 'HS020'})


def analyze(source: str) -> list:
    module = ParsedModule(Path('<snippet>'), source, ast.parse(source))
    return Analyzer(module, Thresholds()).run()


def test_deleted_ids_are_absent_from_signal_name() -> None:
    assert DELETED_IDS.isdisjoint(SignalName.__members__)


def test_deleted_ids_are_absent_from_catalog() -> None:
    assert DELETED_IDS.isdisjoint(RULES)


def test_future_annotations_import_yields_no_finding() -> None:
    findings = analyze(fixtures.FUTURE_ANNOTATIONS)
    assert not any(finding.rule.rule_id == 'HS020' for finding in findings)
    assert not findings


def test_other_future_features_still_yield_no_finding() -> None:
    findings = analyze(fixtures.FUTURE_OTHER_FEATURE)
    assert not findings


def test_ast_and_tokenize_are_confined_to_analysis() -> None:
    offenders = []
    for path in sorted(SRC_ROOT.rglob('*.py')):
        relative = path.relative_to(SRC_ROOT)
        if relative.parts[0] == 'analysis':
            continue
        tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = {alias.name for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {node.module} if node.module else set()
            else:
                continue
            if names & {'ast', 'tokenize'}:
                offenders.append((str(relative), names))
    assert not offenders
