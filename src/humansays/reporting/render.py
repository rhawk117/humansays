"""Rendering.

Text output goes through rich when it is installed (the ``terminal`` extra);
otherwise it falls back to plain ANSI. JSON stays plain so it survives a pipe.
"""

import dataclasses
import json
import sys
from types import SimpleNamespace
from typing import TYPE_CHECKING

from humansays.config.models import Report
from humansays.const import GRADE_STYLES, SEVERITY_STYLES
from humansays.enums import OutputFormat
from humansays.findings.models import Score

from . import ansi
from .grouping import Target, review_targets, shown_targets
from .models import ReportRequest, ScanResult

if TYPE_CHECKING:
    from rich.table import Table
    from rich.text import Text

__all__ = ('json_payload', 'write_report')


def _load_rich() -> SimpleNamespace | None:
    """Sole point of contact with the optional ``terminal`` extra.

    Every other function in this module receives rich's classes as a
    parameter instead of importing them itself, so there is exactly one
    lazy import in this module, not one per rendering helper.
    """
    try:
        from rich.console import Console  # noqa: PLC0415
        from rich.table import Table  # noqa: PLC0415
        from rich.text import Text  # noqa: PLC0415
    except ImportError:
        return None
    return SimpleNamespace(Console=Console, Table=Table, Text=Text)


def _rich_score_line(score: Score, rich: SimpleNamespace) -> 'Text':
    score_line = rich.Text('score ', style='dim')
    score_line.append(f'{score.value}', style=GRADE_STYLES.get(score.grade, ''))
    score_line.append(f' ({score.grade})', style=GRADE_STYLES.get(score.grade, ''))
    score_line.append(
        f'  penalty {score.penalty} over {score.lines} lines'
        f'  density {score.density}/100 lines',
        style='dim',
    )
    return score_line


def _rich_targets_table(shown: list[Target], rich: SimpleNamespace) -> 'Table | None':
    if not shown:
        return None
    table = rich.Table(show_edge=False, pad_edge=False, header_style='dim')
    table.add_column('location', overflow='fold')
    table.add_column('symbol', overflow='fold')
    table.add_column('signals', overflow='fold')
    for target in shown:
        table.add_row(
            f'{target["path"]}:{target["line"]}-{target["end_line"]}',
            target['symbol'],
            _rich_indicator_text(target, rich),
        )
    return table


def _render_rich(request: ReportRequest) -> None:
    rich = _load_rich()
    if rich is None:
        raise RuntimeError(
            '_render_rich is only called after write_report() confirms rich is installed'
        )
    result = request.result
    limit = request.settings.limit
    console = rich.Console(stderr=request.failed)
    targets = review_targets(result.reports)
    shown = shown_targets(targets, limit)

    console.print(
        f'[bold]Python investigation targets[/bold] [dim]{result.label}[/dim]',
        highlight=False,
    )
    console.print(
        f'[dim]files={len(result.reports)} lines={result.lines} '
        f'targets={len(targets)} errors={len(result.errors)}[/dim]',
        highlight=False,
    )
    console.print(_rich_score_line(request.score, rich))

    table = _rich_targets_table(shown, rich)
    if table is not None:
        console.print(table)

    if limit and len(targets) > limit:
        remaining = len(targets) - limit
        console.print(
            f'[dim]truncated={remaining}; use --limit 0 for all targets[/dim]',
            highlight=False,
        )
    for error in result.errors:
        console.print(f'[red]parse-error[/red] {error}', highlight=False)
    if not targets and not result.errors:
        console.print('No suspicious structural indicators found.')


def _rich_indicator_text(target: Target, rich: SimpleNamespace) -> 'Text':
    text = rich.Text()
    seen: set[str] = set()
    for signal in target['signals']:
        indicator = str(signal['rule']['signal'])
        if indicator in seen:
            continue
        seen.add(indicator)
        if text:
            text.append(' ')
        style = SEVERITY_STYLES.get(signal['rule']['severity'], '')
        text.append(indicator, style=style)
    return text


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


def write_report(request: ReportRequest) -> None:
    """Render the report, sending it to stderr when the run failed."""
    if request.settings.format is OutputFormat.JSON:
        stream = sys.stderr if request.failed else sys.stdout
        payload = json_payload(request.result, request.score, request.settings)
        print(json.dumps(payload, indent=2), file=stream)
        return

    if _load_rich() is None:
        ansi.render_text_plain(request)
        return

    _render_rich(request)
