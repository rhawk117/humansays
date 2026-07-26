import ast
from pathlib import Path

import poc_fixtures as fixtures
import pytest

from humansays.analysis.models import ParsedModule
from humansays.analysis.rules import Analyzer
from humansays.config.models import Report, Thresholds
from humansays.findings.models import Score
from humansays.reporting import ansi, render
from humansays.reporting.models import FileReport, ScanResult
from humansays.scoring import score_for

SNAPSHOT = """\
Python investigation targets snippet.py
files=1 lines=11 targets=1 errors=0
score 26.1 (F)  penalty 2.34 over 11 lines  density 21.273/100 lines
snippet.py:10-11  Store  many-base-classes
"""


def _scan_result() -> tuple[ScanResult, Score]:
    source = fixtures.MULTIPLE_INHERITANCE
    module = ParsedModule(Path('snippet.py'), source, ast.parse(source))
    findings = Analyzer(module, Thresholds()).run()
    report = FileReport(
        Path('snippet.py'), len(source.splitlines()), 0, 0, set(), findings
    )
    result = ScanResult('snippet.py', [report], [])
    return result, score_for(result)


def test_plain_text_snapshot_is_stable(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv('NO_COLOR', '1')
    result, score = _scan_result()
    ansi.render_text_plain(result, score, Report(limit=0))
    assert capsys.readouterr().out == SNAPSHOT


def test_emit_falls_back_to_ansi_when_rich_is_absent(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv('NO_COLOR', '1')
    monkeypatch.setattr(render, '_load_rich', lambda: None)
    result, score = _scan_result()
    render.emit(result, score, Report(limit=0))
    assert capsys.readouterr().out == SNAPSHOT
