"""The text report's exact bytes, and where they are written.

Colour is switched off by constructing the attributes or the console's
environment directly. A test that inherits `NO_COLOR` from the shell running
pytest is a test that passes for the wrong reason.
"""

from __future__ import annotations

import ast
import io
import re
from pathlib import Path
from typing import TYPE_CHECKING

from humansays.analysis.extraction import extract
from humansays.analysis.models import ParsedModule
from humansays.config.models import Report, Thresholds
from humansays.const import GRADE_STYLES, SEVERITY_STYLES
from humansays.enums import Grade, OutputFormat, Severity
from humansays.reporting import render
from humansays.reporting.ansi import ANSI_CODES, RESET
from humansays.reporting.console import Console, Destination
from humansays.reporting.models import FileReport, ReportRequest, ScanResult
from humansays.reporting.renderers import AnsiRenderer
from humansays.reporting.terminal import TerminalAttributes
from humansays.scoring import score_for
from humansays.signals import evaluate
from tests.fixtures import sources

if TYPE_CHECKING:
    import pytest
    from pytest_mock import MockerFixture

    from humansays.findings.models import Score

SNAPSHOT = """\
Python investigation targets snippet.py
files=1 lines=11 targets=1 errors=0
score 26.1 (F)  penalty 2.34 over 11 lines  density 21.273/100 lines
snippet.py:10-11  Store  many-base-classes
"""

PLAIN = TerminalAttributes(is_tty=False, no_color=True, force_color=False)
COLOURED = TerminalAttributes(is_tty=True, no_color=False, force_color=True)
NO_COLOR_ENV = {'NO_COLOR': '1'}


class _StdoutOnlyNoColorConsole(Console):
    """Stands in for ``humansays src/ > report.txt`` run from a terminal."""

    def attributes(self, destination: Destination) -> TerminalAttributes:
        return PLAIN if destination is Destination.STDOUT else COLOURED


def _scan_result() -> tuple[ScanResult, Score]:
    source = sources.MULTIPLE_INHERITANCE
    module = ParsedModule(Path('snippet.py'), source, ast.parse(source))
    findings = evaluate(extract(module), Thresholds())
    report = FileReport(
        Path('snippet.py'), len(source.splitlines()), 0, 0, set(), findings
    )
    result = ScanResult('snippet.py', [report], [])
    return result, score_for(result)


def _request(
    exit_code: int, output_format: OutputFormat = OutputFormat.TEXT
) -> ReportRequest:
    result, score = _scan_result()
    return ReportRequest(result, score, Report(limit=0, format=output_format), exit_code)


class TestColouredOutput:
    """The only tests that assert an actual escape byte."""

    def test_the_renderer_emits_escapes_when_attributes_say_so(self) -> None:
        rendered = AnsiRenderer()(_request(0), COLOURED)
        assert RESET in rendered
        assert ANSI_CODES['dim'] in rendered

    def test_the_renderer_emits_none_when_they_do_not(self) -> None:
        assert '\x1b' not in AnsiRenderer()(_request(0), PLAIN)

    def test_stripping_the_escapes_gives_the_plain_report(self) -> None:
        coloured = AnsiRenderer()(_request(0), COLOURED)
        stripped = re.sub(r'\x1b\[[0-9;]*m', '', coloured)
        assert stripped == AnsiRenderer()(_request(0), PLAIN)

    def test_severity_and_grade_styles_reach_the_output(self) -> None:
        rendered = AnsiRenderer()(_request(0), COLOURED)
        assert ANSI_CODES[GRADE_STYLES[Grade.F]] in rendered
        assert ANSI_CODES[SEVERITY_STYLES[Severity.WARNING]] in rendered


def test_plain_text_snapshot_is_stable() -> None:
    # The `+ '\n'` pins the single newline the console adds.
    assert AnsiRenderer()(_request(0), PLAIN) + '\n' == SNAPSHOT


class TestRouting:
    def test_a_passing_text_run_goes_to_stdout(self) -> None:
        assert render.destination_for(_request(0)) is Destination.STDOUT

    def test_a_failing_text_run_goes_to_stderr(self) -> None:
        assert render.destination_for(_request(1)) is Destination.STDERR

    def test_json_goes_to_stdout_even_when_the_run_failed(self) -> None:
        request = _request(1, OutputFormat.JSON)
        assert render.destination_for(request) is Destination.STDOUT


class TestWriteReport:
    def test_the_whole_report_goes_to_stdout(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        render.write_report(_request(0), Console(NO_COLOR_ENV))
        assert capsys.readouterr().out == SNAPSHOT

    def test_the_report_goes_to_stderr_when_the_run_fails(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        render.write_report(_request(1), Console(NO_COLOR_ENV))
        captured = capsys.readouterr()
        assert captured.err == SNAPSHOT
        assert captured.out == ''

    def test_the_renderer_sees_the_destination_stream_not_stdout(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A failing text run must be coloured by stderr's attributes."""
        render.write_report(_request(1), _StdoutOnlyNoColorConsole({}))
        assert RESET in capsys.readouterr().err

    def test_a_passing_run_is_coloured_by_stdout(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        render.write_report(_request(0), Console({'FORCE_COLOR': '1'}))
        assert RESET in capsys.readouterr().out


class TestConsoleEmit:
    def test_emit_writes_exactly_once(self, mocker: MockerFixture) -> None:
        stream = io.StringIO()
        write = mocker.patch.object(stream, 'write', wraps=stream.write)
        mocker.patch('sys.stdout', stream)

        Console({}).emit('one\ntwo', Destination.STDOUT)

        assert write.call_count == 1
        assert write.call_args.args == ('one\ntwo\n',)

    def test_a_broken_pipe_ends_quietly(self, mocker: MockerFixture) -> None:
        stream = mocker.Mock()
        stream.write.side_effect = BrokenPipeError
        mocker.patch('sys.stdout', stream)

        Console({}).emit('report', Destination.STDOUT)

    def test_stderr_is_flushed_before_the_report_reaches_stdout(
        self, mocker: MockerFixture
    ) -> None:
        calls: list[str] = []
        err, out = mocker.Mock(), mocker.Mock()
        err.flush.side_effect = lambda: calls.append('stderr.flush')
        out.write.side_effect = lambda _: calls.append('stdout.write')
        out.flush.side_effect = lambda: calls.append('stdout.flush')
        mocker.patch('sys.stderr', err)
        mocker.patch('sys.stdout', out)

        Console({}).emit('report', Destination.STDOUT)

        assert calls == ['stderr.flush', 'stdout.write', 'stdout.flush']

    def test_streams_are_resolved_at_write_time(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        console = Console({})
        capsys.readouterr()
        console.message('diagnostic')
        assert capsys.readouterr().err == 'diagnostic\n'
