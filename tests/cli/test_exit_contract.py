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
