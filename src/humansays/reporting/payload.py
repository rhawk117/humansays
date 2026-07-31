"""The JSON report's shape.

Kept apart from ``renderers`` and ``render`` so both can import it without
importing each other. ``lint-imports`` rejects the cycle.
"""

import json

from humansays.config.models import Report
from humansays.const import EXIT_REASONS
from humansays.findings.models import Score, field_values
from humansays.reporting.grouping import review_targets, shown_targets
from humansays.reporting.models import ReportRequest, ScanResult

__all__ = ('json_payload', 'report_json', 'status')


def json_payload(result: ScanResult, score: Score, settings: Report) -> dict:
    targets = review_targets(result.reports, show_evidence=settings.show_evidence)
    shown = shown_targets(targets, settings.limit)
    return {
        'schema_version': 1,
        'root': result.label,
        'score': field_values(score),
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


def status(request: ReportRequest) -> dict:
    return {
        'ok': request.exit_code == 0,
        'exit_code': request.exit_code,
        'reason': EXIT_REASONS.get(request.exit_code, 'unknown'),
        'unanalyzed': len(request.result.errors),
    }


def report_json(request: ReportRequest) -> str:
    payload = json_payload(request.result, request.score, request.settings)
    payload['status'] = status(request)
    return json.dumps(payload, indent=2, sort_keys=True)
