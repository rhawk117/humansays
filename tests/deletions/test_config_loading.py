import io

from humansays.cli import main


def test_missing_config_exits_four() -> None:
    code = main(['--config', '/nonexistent/x.toml', '-'], io.StringIO(''))
    assert code == 4
