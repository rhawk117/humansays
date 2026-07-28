"""What one stream can do, observed once.

Build one per stream, never one per process: a run with stdout redirected to a
file and stderr still on a terminal has two different answers. Both colour
variables are read for truthiness, not presence, and the precedence is the
NO_COLOR convention (https://no-color.org).
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Self, TextIO


@dataclass(frozen=True, slots=True)
class TerminalAttributes:
    is_tty: bool
    no_color: bool
    force_color: bool

    @property
    def color(self) -> bool:
        if self.no_color:
            return False

        if self.force_color:
            return True

        return self.is_tty

    @classmethod
    def detect(cls, stream: TextIO, env: Mapping[str, str]) -> Self:
        return cls(
            is_tty=stream.isatty(),
            no_color=bool(env.get('NO_COLOR')) or env.get('TERM') == 'dumb',
            force_color=bool(env.get('FORCE_COLOR')),
        )
