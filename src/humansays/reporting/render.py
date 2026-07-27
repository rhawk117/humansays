"""Rendering.

Every format builds the whole report as one string before anything is written,
so a run produces exactly one write. ``write_report`` below is the only place
in the package that touches a stream.
"""

import dataclasses
import json
import sys

from humansays.config.models import Report
from humansays.const import EXIT_REASONS
from humansays.enums import OutputFormat
from humansays.findings.models import Score
from humansays.reporting import ansi
from humansays.reporting.grouping import review_targets, shown_targets
from humansays.reporting.models import ReportRequest, ScanResult

__all__ = ('json_payload', 'write_report')


def json_payload(result: ScanResult, score: Score, settings: Report) -> dict:
    targets = review_targets(result.reports)
    shown = shown_targets(targets, settings.limit)
    return {
        'schema_version': 1,
        'root': result.label,
        'score': dataclasses.asdict(score),
        'summary': {
            'files': len(result.reports),
            'lines': result.lines,
            'targets': len(targets),
            'signals': sum(len(target['signals']) for target in targets),
            'errors': len(result.errors),
            'truncated': max(0, len(targets) - len(shown)),
        },
        'targets': shown,
        'errors': result.errors,
    }


def _status(request: ReportRequest) -> dict:
    return {
        'ok': request.exit_code == 0,
        'exit_code': request.exit_code,
        'reason': EXIT_REASONS.get(request.exit_code, 'unknown'),
        'unanalyzed': len(request.result.errors),
    }


def report_text(request: ReportRequest, *, is_tty: bool) -> str:
    """The whole report as one string, ready to be written."""
    if request.settings.format is OutputFormat.JSON:
        payload = json_payload(request.result, request.score, request.settings)
        payload['status'] = _status(request)
        return json.dumps(payload, indent=2, sort_keys=True)

    color = ansi.use_color(is_tty=is_tty)
    return '\n'.join(ansi.report_lines(request, color=color))


def write_report(request: ReportRequest) -> None:
    """Flush the report in a single write.

    A failed *text* run goes to stderr, so it leaves stdout clean for whatever
    reads the command's output. JSON always goes to stdout: a machine consumer
    wants the report most on the run that failed, and piping it to stderr made
    ``humansays --format json | jq`` silently empty in exactly that case.
    """
    if request.settings.format is OutputFormat.JSON:
        stream = sys.stdout
    else:
        stream = sys.stderr if request.failed else sys.stdout

    print(report_text(request, is_tty=stream.isatty()), file=stream)
