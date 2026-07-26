"""Grouping and rendering.

Findings are grouped into review targets — one symbol in one file with every
signal that fired against it — ordered so the densest warning clusters come
first. Text output goes through rich; JSON stays plain so it survives a pipe.
"""

import json
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.text import Text

from .const import GRADE_STYLES, SEVERITY_ORDER, SEVERITY_STYLES, UNKNOWN_SEVERITY_ORDER
from .enums import OutputFormat
from .models import FileReport, Report, ScanResult, Score

Target = dict[str, Any]


def signal_sort_key(signal: Target) -> tuple[int, str]:
    order = SEVERITY_ORDER.get(signal["severity"], UNKNOWN_SEVERITY_ORDER)
    return (order, signal["rule_id"])


def target_sort_key(target: Target) -> tuple[int, int, str, int]:
    best = min(
        SEVERITY_ORDER.get(signal["severity"], UNKNOWN_SEVERITY_ORDER)
        for signal in target["signals"]
    )
    return (best, -len(target["signals"]), target["path"], target["line"])


def new_target(report: FileReport, symbol: str, line: int) -> Target:
    return {
        "path": str(report.path),
        "symbol": symbol,
        "line": line,
        "end_line": line,
        "signals": [],
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
            target["line"] = min(target["line"], location.line)
            target["end_line"] = max(target["end_line"], location.end_line)
            target["signals"].append({
                "rule_id": finding.rule.rule_id,
                "indicator": finding.rule.signal,
                "severity": finding.rule.severity,
                "confidence": finding.rule.confidence,
                "weight": finding.rule.weight,
                "message": finding.observation.message,
                "evidence": list(finding.observation.evidence),
                "review_question": finding.rule.review_question,
            })
    targets = list(grouped.values())
    for target in targets:
        target["signals"].sort(key=signal_sort_key)
    targets.sort(key=target_sort_key)
    return targets


def shown_targets(targets: list[Target], limit: int) -> list[Target]:
    return targets if limit == 0 else targets[:limit]


def indicator_text(target: Target) -> Text:
    text = Text()
    seen: set[str] = set()
    for signal in target["signals"]:
        indicator = str(signal["indicator"])
        if indicator in seen:
            continue
        seen.add(indicator)
        if text:
            text.append(" ")
        text.append(indicator, style=SEVERITY_STYLES.get(signal["severity"], ""))
    return text


def score_text(score: Score) -> Text:
    text = Text("score ", style="dim")
    text.append(f"{score.value}", style=GRADE_STYLES.get(score.grade, ""))
    text.append(f" ({score.grade})", style=GRADE_STYLES.get(score.grade, ""))
    text.append(
        f"  penalty {score.penalty} over {score.lines} lines"
        f"  density {score.density}/100 lines",
        style="dim",
    )
    return text


def build_table(targets: list[Target]) -> Table:
    table = Table(show_edge=False, pad_edge=False, header_style="dim")
    table.add_column("location", overflow="fold")
    table.add_column("symbol", overflow="fold")
    table.add_column("signals", overflow="fold")
    for target in targets:
        location = f"{target['path']}:{target['line']}-{target['end_line']}"
        table.add_row(location, target["symbol"], indicator_text(target))
    return table


def render_text(result: ScanResult, score: Score, settings: Report) -> None:
    console = Console()
    targets = review_targets(result.reports)
    shown = shown_targets(targets, settings.limit)
    console.print(
        f"[bold]Python investigation targets[/bold] [dim]{result.label}[/dim]",
        highlight=False,
    )
    console.print(
        f"[dim]files={len(result.reports)} lines={result.lines} "
        f"targets={len(targets)} errors={len(result.errors)}[/dim]",
        highlight=False,
    )
    console.print(score_text(score))
    if shown:
        console.print(build_table(shown))
    if settings.limit and len(targets) > settings.limit:
        remaining = len(targets) - settings.limit
        console.print(
            f"[dim]truncated={remaining}; use --limit 0 for all targets[/dim]",
            highlight=False,
        )
    for error in result.errors:
        console.print(f"[red]parse-error[/red] {error}", highlight=False)
    if not targets and not result.errors:
        console.print("No suspicious structural indicators found.")


def json_payload(result: ScanResult, score: Score, settings: Report) -> dict:
    targets = review_targets(result.reports)
    shown = shown_targets(targets, settings.limit)
    return {
        "schema_version": 4,
        "root": result.label,
        "score": score.model_dump(mode="json"),
        "summary": {
            "files": len(result.reports),
            "lines": result.lines,
            "targets": len(targets),
            "signals": sum(len(target["signals"]) for target in targets),
            "errors": len(result.errors),
            "truncated": max(0, len(targets) - len(shown)),
        },
        "targets": shown,
        "errors": result.errors,
    }


def emit(result: ScanResult, score: Score, settings: Report) -> None:
    if settings.format is OutputFormat.JSON:
        print(json.dumps(json_payload(result, score, settings), indent=2))
        return
    render_text(result, score, settings)
