"""The colour decision, and the environment reading that feeds it."""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

from humansays.reporting.terminal import TerminalAttributes

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def attributes(*, is_tty: bool, no_color: bool, force_color: bool) -> TerminalAttributes:
    return TerminalAttributes(is_tty=is_tty, no_color=no_color, force_color=force_color)


class TestColorPrecedence:
    def test_no_color_disables_color(self) -> None:
        assert attributes(is_tty=True, no_color=True, force_color=False).color is False

    def test_no_color_beats_force_color(self) -> None:
        assert attributes(is_tty=True, no_color=True, force_color=True).color is False

    def test_force_color_overrides_non_tty(self) -> None:
        assert attributes(is_tty=False, no_color=False, force_color=True).color is True

    def test_a_plain_tty_gets_color(self) -> None:
        assert attributes(is_tty=True, no_color=False, force_color=False).color is True

    def test_a_plain_pipe_does_not(self) -> None:
        assert attributes(is_tty=False, no_color=False, force_color=False).color is False


class TestDetect:
    def test_term_dumb_disables(self) -> None:
        detected = TerminalAttributes.detect(io.StringIO(), {'TERM': 'dumb'})
        assert detected.no_color is True
        assert detected.color is False

    def test_no_color_is_read_for_truthiness_not_presence(self) -> None:
        detected = TerminalAttributes.detect(
            io.StringIO(), {'NO_COLOR': '', 'FORCE_COLOR': '1'}
        )
        assert detected.no_color is False
        assert detected.color is True

    def test_a_term_other_than_dumb_does_not_disable(self) -> None:
        detected = TerminalAttributes.detect(
            io.StringIO(), {'TERM': 'xterm-256color', 'FORCE_COLOR': '1'}
        )
        assert detected.no_color is False
        assert detected.color is True

    def test_a_tty_stream_is_detected_as_one(self, mocker: MockerFixture) -> None:
        stream = mocker.Mock()
        stream.isatty.return_value = True
        detected = TerminalAttributes.detect(stream, {})
        assert detected.is_tty is True
        assert detected.color is True

    def test_a_non_tty_stream_gets_no_colour(self, mocker: MockerFixture) -> None:
        stream = mocker.Mock()
        stream.isatty.return_value = False
        assert TerminalAttributes.detect(stream, {}).color is False

    def test_an_empty_environment_falls_back_to_the_stream(self) -> None:
        detected = TerminalAttributes.detect(io.StringIO(), {})
        assert detected == TerminalAttributes(
            is_tty=False, no_color=False, force_color=False
        )
