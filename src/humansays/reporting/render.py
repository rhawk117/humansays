"""Rendering.

Text output goes through rich when it is installed (the ``terminal`` extra);
otherwise it falls back to plain ANSI. JSON stays plain so it survives a pipe.
"""

import dataclasses
import json
from types import SimpleNamespace
from typing import TYPE_CHECKING

from humansays.config.models import Report
from humansays.const import GRADE_STYLES, SEVERITY_STYLES
from humansays.enums import OutputFormat
from humansays.findings.models import Score

from . import ansi
from .grouping import Target, review_targets, shown_targets
from .models import ScanResult

if TYPE_CHECKING:
    from rich.table import Table
    from rich.text import Text

__all__ = ('emit', 'json_payload')


def _load_rich() -> SimpleNamespace | None:
    """Sole point of contact with the optional ``terminal`` extra.

    Every other function in this module receives rich's classes as a
    parameter instead of importing them itself, so there is exactly one
    lazy import in this module, not one per rendering helper.
    """
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.text import Text
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


def _render_rich(result: ScanResult, score: Score, settings: Report) -> None:
    rich = _load_rich()
    if rich is None:
        raise RuntimeError(
            '_render_rich is only called after emit() confirms rich is installed'
        )
    console = rich.Console()
    targets = review_targets(result.reports)
    shown = shown_targets(targets, settings.limit)

    console.print(
        f'[bold]Python investigation targets[/bold] [dim]{result.label}[/dim]',
        highlight=False,
    )
    console.print(
        f'[dim]files={len(result.reports)} lines={result.lines} '
        f'targets={len(targets)} errors={len(result.errors)}[/dim]',
        highlight=False,
    )
    console.print(_rich_score_line(score, rich))

    table = _rich_targets_table(shown, rich)
    if table is not None:
        console.print(table)

    if settings.limit and len(targets) > settings.limit:
        remaining = len(targets) - settings.limit
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
        indicator = str(signal['indicator'])
        if indicator in seen:
            continue
        seen.add(indicator)
        if text:
            text.append(' ')
        text.append(indicator, style=SEVERITY_STYLES.get(signal['severity'], ''))
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


def emit(result: ScanResult, score: Score, settings: Report) -> None:
    if settings.format is OutputFormat.JSON:
        print(json.dumps(json_payload(result, score, settings), indent=2))
        return
    if _load_rich() is None:
        ansi.render_text_plain(result, score, settings)
        return
    _render_rich(result, score, settings)
