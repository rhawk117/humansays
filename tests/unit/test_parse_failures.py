"""Reporting files that could not be parsed."""

from __future__ import annotations

import platform
from typing import TYPE_CHECKING

from humansays.application import analyze_paths, is_version_candidate, parse_failure
from humansays.config.models import ScannerSettings
from humansays.const import UNPARSED_HINT_TEMPLATE
from humansays.reporting import ansi
from humansays.reporting.models import ScanResult

if TYPE_CHECKING:
    from pathlib import Path


def _syntax_error(source: str) -> SyntaxError:
    try:
        compile(source, 'broken.py', 'exec')
    except SyntaxError as error:
        return error

    raise AssertionError('expected a SyntaxError')


def _lineless_error() -> SyntaxError:
    # Built, not provoked: a NUL byte raises ValueError on 3.11 and
    # SyntaxError on 3.12+, and the shape under test is `lineno is None`.
    return SyntaxError('source code string cannot contain null bytes')


class TestParseFailureMessage:
    def test_it_is_one_line(self) -> None:
        assert '\n' not in parse_failure(_syntax_error('def (:\n'))

    def test_it_names_the_line(self) -> None:
        assert '(line 2)' in parse_failure(_syntax_error('x = 1\ndef (:\n'))

    def test_it_does_not_repeat_the_filename(self) -> None:
        assert 'broken.py' not in parse_failure(_syntax_error('def (:\n'))


class TestFailuresWithoutALine:
    def test_no_line_suffix_when_there_is_no_line(self) -> None:
        error = _lineless_error()
        assert error.lineno is None
        assert parse_failure(error) == (
            'cannot parse: source code string cannot contain null bytes'
        )
        assert 'None' not in parse_failure(error)

    def test_it_is_not_a_version_candidate(self) -> None:
        assert is_version_candidate(_lineless_error()) is False

    def test_a_syntax_error_with_a_line_is_a_version_candidate(self) -> None:
        assert is_version_candidate(_syntax_error('def (:\n')) is True


class TestAnalyzePathsPopulatesUnparsed:
    def test_a_broken_file_is_counted(self, tmp_path: Path) -> None:
        (tmp_path / 'bad.py').write_text('def (:\n', encoding='utf-8')
        result = analyze_paths([tmp_path / 'bad.py'], ScannerSettings())
        assert result.unparsed == 1
        assert len(result.errors) == 1

    def test_a_binary_file_is_reported_but_not_counted(self, tmp_path: Path) -> None:
        (tmp_path / 'bin.py').write_bytes(b'x = 1\x00\n')
        result = analyze_paths([tmp_path / 'bin.py'], ScannerSettings())
        assert len(result.errors) == 1
        assert result.unparsed == 0

    def test_a_clean_file_counts_nothing(self, tmp_path: Path) -> None:
        (tmp_path / 'ok.py').write_text('x = 1\n', encoding='utf-8')
        result = analyze_paths([tmp_path / 'ok.py'], ScannerSettings())
        assert result.errors == []
        assert result.unparsed == 0

    def test_the_hint_does_not_appear_for_a_binary_file(self, tmp_path: Path) -> None:
        (tmp_path / 'bin.py').write_bytes(b'x = 1\x00\n')
        result = analyze_paths([tmp_path / 'bin.py'], ScannerSettings())
        rendered = '\n'.join(ansi.unanalyzed_lines(result, color=False))
        assert 'parse-error' in rendered
        assert 'uv tool install' not in rendered


class TestHint:
    def test_the_hint_appears_once_for_many_unparsed_files(self) -> None:
        result = ScanResult(
            'x',
            [],
            [f'a{i}.py: cannot parse: invalid syntax (line 1)' for i in range(200)],
            unparsed=200,
        )
        lines = ansi.unanalyzed_lines(result, color=False)
        hints = [line for line in lines if 'uv tool install' in line]
        assert len(hints) == 1

    def test_the_hint_names_the_running_interpreter(self) -> None:
        result = ScanResult('x', [], ['a.py: cannot parse: bad (line 1)'], unparsed=1)
        rendered = '\n'.join(ansi.unanalyzed_lines(result, color=False))
        assert platform.python_version() in rendered

    def test_no_hint_when_the_failures_are_not_parse_failures(self) -> None:
        result = ScanResult('x', [], ['a.py: [Errno 13] Permission denied'], unparsed=0)
        rendered = '\n'.join(ansi.unanalyzed_lines(result, color=False))
        assert 'uv tool install' not in rendered

    def test_no_output_at_all_when_nothing_failed(self) -> None:
        assert ansi.unanalyzed_lines(ScanResult('x', [], []), color=False) == []

    def test_the_template_states_the_cause_as_a_possibility(self) -> None:
        assert 'If the files above' in UNPARSED_HINT_TEMPLATE
