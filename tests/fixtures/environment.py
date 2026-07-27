"""Terminal-environment fixtures.

`use_color` reads `NO_COLOR`, `FORCE_COLOR` and `TERM` together, so a test that
sets only one of them inherits the other two from whatever shell ran pytest.
Each fixture below pins all three, which is what makes the colour tests give
the same answer under CI as on a developer's terminal.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def no_color(monkeypatch: pytest.MonkeyPatch) -> None:
    """`NO_COLOR` set, with nothing left to override it."""
    monkeypatch.setenv('NO_COLOR', '1')
    monkeypatch.delenv('FORCE_COLOR', raising=False)
    monkeypatch.setenv('TERM', 'xterm-256color')


@pytest.fixture
def forced_color(monkeypatch: pytest.MonkeyPatch) -> None:
    """`FORCE_COLOR` set, so colour survives a non-tty stream."""
    monkeypatch.setenv('FORCE_COLOR', '1')
    monkeypatch.delenv('NO_COLOR', raising=False)
    monkeypatch.setenv('TERM', 'xterm-256color')


@pytest.fixture
def dumb_terminal(monkeypatch: pytest.MonkeyPatch) -> None:
    """`TERM=dumb` with neither override set, so the terminal itself decides."""
    monkeypatch.delenv('NO_COLOR', raising=False)
    monkeypatch.delenv('FORCE_COLOR', raising=False)
    monkeypatch.setenv('TERM', 'dumb')
