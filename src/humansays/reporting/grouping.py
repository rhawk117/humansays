"""Grouping findings into review targets.

A target is one symbol in one file with every signal that fired against it,
ordered so the densest warning clusters come first.
"""

from typing import Any

from humansays.const import SEVERITY_ORDER, UNKNOWN_SEVERITY_ORDER

from .models import FileReport

Target = dict[str, Any]


def signal_sort_key(signal: Target) -> tuple[int, str]:
    order = SEVERITY_ORDER.get(signal['severity'], UNKNOWN_SEVERITY_ORDER)
    return (order, signal['rule_id'])


def target_sort_key(target: Target) -> tuple[int, int, str, int]:
    best = min(
        SEVERITY_ORDER.get(signal['severity'], UNKNOWN_SEVERITY_ORDER)
        for signal in target['signals']
    )
    return (best, -len(target['signals']), target['path'], target['line'])


def new_target(report: FileReport, symbol: str, line: int) -> Target:
    return {
        'path': str(report.path),
        'symbol': symbol,
        'line': line,
        'end_line': line,
        'signals': [],
    }


def review_targets(reports: list[FileReport]) -> list[Target]:
    grouped: dict[tuple[str, str], Target] = {}
    for report in reports:
        for finding in report.findings:
            location = finding.location
            key = (str(report.path), location.symbol)
            if key not in grouped:
                grouped[key] = new_target(report, location.symbol, location.line)
            target = grouped[key]
            target['line'] = min(target['line'], location.line)
            target['end_line'] = max(target['end_line'], location.end_line)
            target['signals'].append({
                'rule_id': finding.rule.rule_id,
                'indicator': finding.rule.signal,
                'severity': finding.rule.severity,
                'confidence': finding.rule.confidence,
                'weight': finding.rule.weight,
                'message': finding.observation.message,
                'evidence': list(finding.observation.evidence),
                'review_question': finding.rule.review_question,
            })
    targets = list(grouped.values())
    for target in targets:
        target['signals'].sort(key=signal_sort_key)
    targets.sort(key=target_sort_key)
    return targets


def shown_targets(targets: list[Target], limit: int) -> list[Target]:
    return targets if limit == 0 else targets[:limit]
