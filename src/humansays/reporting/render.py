"""Routing: which renderer builds the report, and which stream receives it.

A failed text run goes to stderr, leaving stdout clean. JSON always goes to
stdout: routing it to stderr made ``humansays --format json | jq`` silently
empty on exactly the run a machine consumer cares about most.

The renderer gets the attributes of the destination it is actually headed for.
Using stdout's unconditionally would drop colour from a failing text run whose
stdout is redirected but whose stderr is still a terminal.
"""

from humansays.config.models import Report
from humansays.enums import OutputFormat
from humansays.reporting.console import Console, Destination
from humansays.reporting.models import ReportRequest
from humansays.reporting.renderers import AnsiRenderer, JsonRenderer, Renderer

__all__ = ('destination_for', 'renderer_for', 'write_report')


def renderer_for(settings: Report) -> Renderer:
    if settings.format is OutputFormat.JSON:
        return JsonRenderer()

    return AnsiRenderer()


def destination_for(request: ReportRequest) -> Destination:
    if request.settings.format is OutputFormat.JSON:
        return Destination.STDOUT

    return Destination.STDERR if request.failed else Destination.STDOUT


def write_report(request: ReportRequest, console: Console) -> None:
    destination = destination_for(request)
    renderer = renderer_for(request.settings)
    console.emit(renderer(request, console.attributes(destination)), destination)
