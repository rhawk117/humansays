import io
from pathlib import Path

import pytest

from humansays.cli import main


def run(tmp_path: Path, config: str, name: str = 'humansays.toml') -> int:
    source = tmp_path / 'good.py'
    source.write_text('def ok(a):\n    return a\n')
    path = tmp_path / name
    path.write_text(config)
    return main(['--config', str(path), str(source)], io.StringIO(''))


@pytest.mark.parametrize(
    ('label', 'config'),
    [
        ('malformed toml', '[report\nlimit = 5\n'),
        ('unknown key', 'not_a_key = 5\n'),
        ('wrong value type', 'report = { limit = "abc" }\n'),
        ('bad enum value', 'report = { format = "xml" }\n'),
        ('non-mapping nested', 'report = 5\n'),
        ('out of range', 'report = { min_score = 200.0 }\n'),
    ],
)
def test_config_errors_exit_four(tmp_path: Path, label: str, config: str) -> None:
    assert run(tmp_path, config) == 4


def test_config_error_reports_cleanly(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(tmp_path, 'not_a_key = 5\n') == 4
    captured = capsys.readouterr()
    assert captured.err.startswith('error: ')
    assert 'Traceback' not in captured.err


def test_tool_prefix_in_humansays_toml_is_explained(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(tmp_path, '[tool.humansays]\nlimit = 5\n') == 4
    message = capsys.readouterr().err
    assert 'top level' in message
    assert 'pyproject.toml' in message


def test_pyproject_still_unwraps_the_tool_section(tmp_path: Path) -> None:
    config = '[tool.humansays]\n[tool.humansays.report]\nlimit = 5\n'
    assert run(tmp_path, config, name='pyproject.toml') == 0


def test_valid_flat_config_still_loads(tmp_path: Path) -> None:
    assert run(tmp_path, 'report = { limit = 5 }\n') == 0


def test_unexpected_errors_exit_seventy(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def explode(*args: object, **kwargs: object) -> None:
        raise RuntimeError('boom')

    monkeypatch.setattr('humansays.cli.application.collect_files', explode)
    source = tmp_path / 'good.py'
    source.write_text('def ok(a):\n    return a\n')

    code = main([str(source)], io.StringIO(''))

    assert code == 70
    assert 'internal error' in capsys.readouterr().err


def test_help_still_exits_zero() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(['--help'], io.StringIO(''))

    assert excinfo.value.code == 0


BROKEN = 'def broken(\n'
CLEAN = 'def ok(a):\n    return a\n'


def test_only_unanalyzed_input_exits_five(tmp_path: Path) -> None:
    (tmp_path / 'bad.py').write_text(BROKEN)
    assert main([str(tmp_path)], io.StringIO('')) == 5


def test_one_unanalyzed_file_among_many_exits_five(tmp_path: Path) -> None:
    (tmp_path / 'bad.py').write_text(BROKEN)
    (tmp_path / 'good.py').write_text(CLEAN)
    assert main([str(tmp_path)], io.StringIO('')) == 5


def test_unreadable_file_exits_five(tmp_path: Path) -> None:
    blocked = tmp_path / 'blocked.py'
    blocked.write_text(CLEAN)
    blocked.chmod(0o000)
    try:
        assert main([str(tmp_path)], io.StringIO('')) == 5
    finally:
        blocked.chmod(0o644)


def test_invalid_utf8_exits_five(tmp_path: Path) -> None:
    (tmp_path / 'bad.py').write_bytes(b'x = "\xff\xfe"\n')
    assert main([str(tmp_path)], io.StringIO('')) == 5


def test_findings_win_over_unanalyzed(tmp_path: Path) -> None:
    (tmp_path / 'bad.py').write_text(BROKEN)
    (tmp_path / 'wide.py').write_text('def wide(a, b, c, d, e, f):\n    return a\n')
    code = main(['--fail-on', 'any', str(tmp_path)], io.StringIO(''))
    assert code == 1


def test_clean_scan_still_exits_zero(tmp_path: Path) -> None:
    (tmp_path / 'good.py').write_text(CLEAN)
    assert main([str(tmp_path)], io.StringIO('')) == 0
