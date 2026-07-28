"""Turning a scan into text.

A renderer receives the run and the capabilities of the stream the text is
headed for, and returns the whole report as one string. It never learns which
stream that is and never writes; ``console`` does both.
"""

from typing import Protocol

from humansays.reporting import ansi
from humansays.reporting.models import ReportRequest
from humansays.reporting.payload import report_json
from humansays.reporting.terminal import TerminalAttributes


class Renderer(Protocol):
    def __call__(self, request: ReportRequest, attributes: TerminalAttributes) -> str: ...


class JsonRenderer:
    def __call__(self, request: ReportRequest, attributes: TerminalAttributes) -> str:
        del attributes
        return report_json(request)


class AnsiRenderer:
    def __call__(self, request: ReportRequest, attributes: TerminalAttributes) -> str:
        return '\n'.join(ansi.report_lines(request, color=attributes.color))
