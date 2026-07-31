"""Building the text report.

Nothing here writes anything. ``report_lines`` returns the whole report; the
console joins it and emits it in one call.
"""

import platform
from types import MappingProxyType

from humansays.const import GRADE_STYLES, SEVERITY_STYLES, UNPARSED_HINT_TEMPLATE
from humansays.findings.models import Score
from humansays.reporting.grouping import Target, review_targets, shown_targets
from humansays.reporting.models import ReportRequest, ScanResult

RESET = '\x1b[0m'
ANSI_CODES = MappingProxyType({
    'bold yellow': '\x1b[1;33m',
    'bold green': '\x1b[1;32m',
    'bold red': '\x1b[1;31m',
    'green': '\x1b[32m',
    'yellow': '\x1b[33m',
    'cyan': '\x1b[36m',
    'dim': '\x1b[2m',
    '': '',
})


def _style(text: str, style: str, *, color: bool) -> str:
    if not color or not style:
        return text

    code = ANSI_CODES.get(style, '')
    return f'{code}{text}{RESET}' if code else text


def indicator_text(target: Target, *, color: bool) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for signal in target['signals']:
        indicator = str(signal['rule']['signal'])
        if indicator in seen:
            continue

        seen.add(indicator)
        style = SEVERITY_STYLES.get(signal['rule']['severity'], '')
        parts.append(_style(indicator, style, color=color))

    return ' '.join(parts)


def score_text(score: Score, *, color: bool) -> str:
    grade_style = GRADE_STYLES.get(score.grade, '')
    value = _style(f'{score.value}', grade_style, color=color)
    grade = _style(f'({score.grade})', grade_style, color=color)
    tail = _style(
        f'penalty {score.penalty} over {score.lines} lines'
        f'  density {score.density}/100 lines',
        'dim',
        color=color,
    )
    label = _style('score ', 'dim', color=color)
    return f'{label}{value} {grade}  {tail}'


def unanalyzed_lines(result: ScanResult, *, color: bool) -> list[str]:
    if not result.errors:
        return []

    analyzed = len(result.reports)
    total = analyzed + len(result.errors)
    lines = [
        _style(
            f'coverage {analyzed} of {total} files analyzed; '
            f'{len(result.errors)} not analyzed - the score covers the '
            f'analyzed files only',
            'bold yellow',
            color=color,
        )
    ]
    lines.extend(
        _style('parse-error', 'bold red', color=color) + f' {error}'
        for error in result.errors
    )

    if result.unparsed:
        hint = UNPARSED_HINT_TEMPLATE.format(version=platform.python_version())
        lines.append(_style(hint, 'dim', color=color))

    return lines


def report_lines(request: ReportRequest, *, color: bool) -> list[str]:
    result = request.result
    limit = request.settings.limit
    targets = review_targets(result.reports, show_evidence=request.settings.show_evidence)
    shown = shown_targets(targets, limit)

    summary = _style(
        f'files={len(result.reports)} lines={result.lines} '
        f'targets={len(targets)} errors={len(result.errors)}',
        'dim',
        color=color,
    )
    lines = [
        f'Python investigation targets {result.label}',
        summary,
        score_text(request.score, color=color),
    ]

    for target in shown:
        location = f'{target["path"]}:{target["line"]}-{target["end_line"]}'
        indicators = indicator_text(target, color=color)
        lines.append(f'{location}  {target["symbol"]}  {indicators}')

    if limit and len(targets) > limit:
        remaining = len(targets) - limit
        message = f'truncated={remaining}; use --limit 0 for all targets'
        lines.append(_style(message, 'dim', color=color))

    lines.extend(unanalyzed_lines(result, color=color))

    if not targets and not result.errors:
        lines.append('No suspicious structural indicators found.')

    return lines
