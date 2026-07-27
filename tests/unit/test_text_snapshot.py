import ast
from pathlib import Path

import pytest

from humansays.analysis.models import ParsedModule
from humansays.analysis.rules import RulesetEvaluator
from humansays.config.models import Report, Thresholds
from humansays.findings.models import Score
from humansays.reporting import render
from humansays.reporting.models import FileReport, ReportRequest, ScanResult
from humansays.scoring import score_for
from tests.fixtures import sources

SNAPSHOT = """\
Python investigation targets snippet.py
files=1 lines=11 targets=1 errors=0
score 26.1 (F)  penalty 2.34 over 11 lines  density 21.273/100 lines
snippet.py:10-11  Store  many-base-classes
"""


def _scan_result() -> tuple[ScanResult, Score]:
    source = sources.MULTIPLE_INHERITANCE
    module = ParsedModule(Path('snippet.py'), source, ast.parse(source))
    findings = RulesetEvaluator(module, Thresholds()).run()
    report = FileReport(
        Path('snippet.py'), len(source.splitlines()), 0, 0, set(), findings
    )
    result = ScanResult('snippet.py', [report], [])
    return result, score_for(result)


def test_plain_text_snapshot_is_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('NO_COLOR', '1')
    result, score = _scan_result()
    request = ReportRequest(result, score, Report(limit=0), 0)
    assert render.report_text(request, is_tty=False) + '\n' == SNAPSHOT


def test_write_report_sends_the_whole_report_to_stdout(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv('NO_COLOR', '1')
    result, score = _scan_result()
    render.write_report(ReportRequest(result, score, Report(limit=0), 0))
    assert capsys.readouterr().out == SNAPSHOT


def test_the_report_goes_to_stderr_when_the_run_fails(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv('NO_COLOR', '1')
    result, score = _scan_result()
    render.write_report(ReportRequest(result, score, Report(limit=0), 1))
    captured = capsys.readouterr()
    assert captured.err == SNAPSHOT
    assert captured.out == ''
