import pytest

from humansays.reporting import ansi


def test_no_color_disables_color(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('NO_COLOR', '1')
    monkeypatch.delenv('FORCE_COLOR', raising=False)
    assert ansi.use_color(is_tty=True) is False


def test_force_color_overrides_non_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('FORCE_COLOR', '1')
    monkeypatch.delenv('NO_COLOR', raising=False)
    assert ansi.use_color(is_tty=False) is True


def test_term_dumb_disables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv('NO_COLOR', raising=False)
    monkeypatch.delenv('FORCE_COLOR', raising=False)
    monkeypatch.setenv('TERM', 'dumb')
    assert ansi.use_color(is_tty=True) is False
