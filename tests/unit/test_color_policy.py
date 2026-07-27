import pytest

from humansays.reporting import ansi


@pytest.mark.usefixtures('no_color')
def test_no_color_disables_color() -> None:
    assert ansi.use_color(is_tty=True) is False


@pytest.mark.usefixtures('forced_color')
def test_force_color_overrides_non_tty() -> None:
    assert ansi.use_color(is_tty=False) is True


@pytest.mark.usefixtures('dumb_terminal')
def test_term_dumb_disables() -> None:
    assert ansi.use_color(is_tty=True) is False
