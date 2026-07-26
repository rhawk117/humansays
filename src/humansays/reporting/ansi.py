"""Plain-ANSI text rendering.

Used instead of rich's console renderer when rich is not installed (the
``terminal`` extra is optional) or when the environment asks for plain output.
Honors the informal ``NO_COLOR``/``FORCE_COLOR`` convention and ``TERM=dumb``.
"""

import os
import sys

from humansays.config.models import Report
from humansays.const import GRADE_STYLES, SEVERITY_STYLES
from humansays.findings.models import Score

from .grouping import Target, review_targets, shown_targets
from .models import ScanResult

RESET = '\x1b[0m'
ANSI_CODES = {
    'bold yellow': '\x1b[1;33m',
    'bold green': '\x1b[1;32m',
    'bold red': '\x1b[1;31m',
    'green': '\x1b[32m',
    'yellow': '\x1b[33m',
    'cyan': '\x1b[36m',
    'dim': '\x1b[2m',
    '': '',
}


def use_color(*, is_tty: bool) -> bool:
    if os.environ.get('NO_COLOR') or os.environ.get('TERM') == 'dumb':
        return False
    if os.environ.get('FORCE_COLOR'):
        return True
    return is_tty


def _style(text: str, style: str, *, color: bool) -> str:
    if not color or not style:
        return text
    code = ANSI_CODES.get(style, '')
    return f'{code}{text}{RESET}' if code else text


def indicator_text(target: Target, *, color: bool) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for signal in target['signals']:
        indicator = str(signal['indicator'])
        if indicator in seen:
            continue
        seen.add(indicator)
        style = SEVERITY_STYLES.get(signal['severity'], '')
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


def render_text_plain(result: ScanResult, score: Score, settings: Report) -> None:
    color = use_color(is_tty=sys.stdout.isatty())
    targets = review_targets(result.reports)
    shown = shown_targets(targets, settings.limit)

    print(f'Python investigation targets {result.label}')
    print(
        _style(
            f'files={len(result.reports)} lines={result.lines} '
            f'targets={len(targets)} errors={len(result.errors)}',
            'dim',
            color=color,
        ),
    )
    print(score_text(score, color=color))
    for target in shown:
        location = f'{target["path"]}:{target["line"]}-{target["end_line"]}'
        print(f'{location}  {target["symbol"]}  {indicator_text(target, color=color)}')
    if settings.limit and len(targets) > settings.limit:
        remaining = len(targets) - settings.limit
        message = f'truncated={remaining}; use --limit 0 for all targets'
        print(_style(message, 'dim', color=color))
    for error in result.errors:
        print(_style('parse-error', 'bold red', color=color) + f' {error}')
    if not targets and not result.errors:
        print('No suspicious structural indicators found.')
