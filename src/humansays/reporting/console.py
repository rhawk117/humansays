"""Where the package writes to a stream.

Every report and every diagnostic goes through ``Console``, by convention
rather than by enforcement; the one exception is the ``StreamHandler`` that
``cli._diagnostics`` attaches to stderr. Streams are resolved at write time
because ``capsys`` and ``redirect_stdout`` replace ``sys.stdout`` per test.

Suppressing ``BrokenPipeError`` is a partial fix for ``humansays . | head``:
CPython flushes stdout again at interpreter shutdown, which can still print
"Exception ignored". Closing that gap needs an entry-point wrapper.
"""

import contextlib
import sys
from collections.abc import Mapping
from enum import Enum
from typing import TextIO

from humansays.reporting.terminal import TerminalAttributes


class Destination(Enum):
    STDOUT = 'stdout'
    STDERR = 'stderr'


class Console:
    def __init__(self, env: Mapping[str, str]) -> None:
        self._env = env

    def _stream(self, destination: Destination) -> TextIO:
        return sys.stdout if destination is Destination.STDOUT else sys.stderr

    def attributes(self, destination: Destination) -> TerminalAttributes:
        return TerminalAttributes.detect(self._stream(destination), self._env)

    def emit(self, text: str, destination: Destination) -> None:
        if destination is Destination.STDOUT:
            sys.stderr.flush()

        stream = self._stream(destination)
        with contextlib.suppress(BrokenPipeError):
            stream.write(f'{text}\n')
            stream.flush()

    def message(self, text: str) -> None:
        self.emit(text, Destination.STDERR)
