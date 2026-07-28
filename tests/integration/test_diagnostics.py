"""Verbosity, the logging channel, and the stdout/stderr split.

The load-bearing property is that stdout carries the report and nothing else at
every verbosity, which ``humansays --format json > report.json`` depends on.
"""

from __future__ import annotations

import contextlib
import io
import json
import logging
from typing import TYPE_CHECKING

import pytest

from humansays.cli import main

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

PACKAGE_LOGGER = 'humansays'


@pytest.fixture(autouse=True)
def reset_package_logger() -> Iterator[None]:
    """Restore the package logger around every test in this module.

    ``pytest-randomly`` reorders tests, so a leaked handler surfaces as an
    unrelated failure elsewhere in the run rather than as a failure here.
    """
    logger = logging.getLogger(PACKAGE_LOGGER)
    handlers = list(logger.handlers)
    level = logger.level
    yield
    logger.handlers = handlers
    logger.setLevel(level)


def run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv, io.StringIO(''))
    return code, out.getvalue(), err.getvalue()


@pytest.fixture
def source(tmp_path: Path) -> str:
    module = tmp_path / 'sample.py'
    module.write_text('def ok(a):\n    return a\n', encoding='utf-8')
    return str(tmp_path)


class TestStdoutIsOnlyTheReport:
    @pytest.mark.parametrize('flags', [[], ['-v'], ['-vv']])
    def test_json_on_stdout_stays_parseable_at_every_verbosity(
        self, source: str, flags: list[str]
    ) -> None:
        code, out, _ = run([source, '--format', 'json', *flags])
        assert code == 0
        assert json.loads(out)['summary']['files'] == 1

    @pytest.mark.parametrize('flags', [[], ['-v'], ['-vv']])
    def test_text_on_stdout_is_only_the_report(
        self, source: str, flags: list[str]
    ) -> None:
        code, out, _ = run([source, '--format', 'text', *flags])
        assert code == 0
        assert out.startswith('Python investigation targets')
        assert 'INFO' not in out
        assert 'collected' not in out

    def test_diagnostics_go_to_stderr_not_stdout(self, source: str) -> None:
        _, out, err = run([source, '--format', 'json', '-vv'])
        assert 'collected 1 files' in err
        assert 'collected' not in out


class TestVerbosity:
    def test_default_verbosity_is_silent(self, source: str) -> None:
        _, _, err = run([source, '--format', 'json'])
        assert err == ''

    def test_v_reports_the_config_and_the_file_counts(self, source: str) -> None:
        _, _, err = run([source, '--format', 'json', '-v'])
        assert 'INFO' in err
        assert 'analyzed 1 of 1 files' in err

    def test_a_parse_failure_is_logged_as_a_warning_from_v_up(
        self, tmp_path: Path
    ) -> None:
        broken = tmp_path / 'broken.py'
        broken.write_text('def (:\n', encoding='utf-8')
        _, _, err = run([str(tmp_path), '--format', 'json', '-v'])
        assert 'WARNING' in err
        assert 'not analyzed' in err

    def test_a_parse_failure_is_not_logged_at_default_verbosity(
        self, tmp_path: Path
    ) -> None:
        broken = tmp_path / 'broken.py'
        broken.write_text('def (:\n', encoding='utf-8')
        _, _, err = run([str(tmp_path), '--format', 'json'])
        assert err == ''


class TestHandlerLifecycle:
    def test_repeated_runs_do_not_accumulate_handlers(self, source: str) -> None:
        logger = logging.getLogger(PACKAGE_LOGGER)
        before = len(logger.handlers)
        for _ in range(3):
            run([source, '--format', 'json', '-vv'])
        assert len(logger.handlers) == before

    def test_the_level_is_restored_after_a_run(self, source: str) -> None:
        logger = logging.getLogger(PACKAGE_LOGGER)
        logger.setLevel(logging.CRITICAL)
        run([source, '--format', 'json', '-vv'])
        assert logger.level == logging.CRITICAL


class TestArgumentParsing:
    def test_help_lists_verbose_and_is_not_the_preparser_stub(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), pytest.raises(SystemExit) as excinfo:
            main(['--help'])
        assert excinfo.value.code == 0
        assert '--verbose' in out.getvalue()
        assert '--min-score' in out.getvalue()

    def test_a_path_named_dash_v_is_still_a_path(self, tmp_path: Path) -> None:
        odd = tmp_path / '-v'
        odd.mkdir()
        (odd / 'm.py').write_text('x = 1\n', encoding='utf-8')
        code, out, _ = run(['--format', 'json', '--', str(odd)])
        assert code == 0
        assert json.loads(out)['summary']['files'] == 1

    def test_vv_says_more_than_v(self, source: str) -> None:
        _, _, single = run([source, '--format', 'json', '-v'])
        _, _, double = run([source, '--format', 'json', '-vv'])
        assert 'DEBUG' not in single
        assert 'DEBUG' in double

    def test_a_malformed_verbose_flag_gets_the_full_usage(self, source: str) -> None:
        err = io.StringIO()
        with contextlib.redirect_stderr(err), pytest.raises(SystemExit):
            main(['--verbose=3', source])
        assert '--min-score' in err.getvalue()

    def test_verbose_never_reaches_the_settings_schema(self, source: str) -> None:
        code, _, _ = run([source, '--format', 'json', '-vv'])
        assert code == 0
