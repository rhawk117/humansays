"""Grouping findings into review targets.

A target is one symbol in one file with every signal that fired against it,
ordered so the densest warning clusters come first.
"""

import dataclasses
from typing import TypedDict, cast

from humansays.const import SEVERITY_ORDER, UNKNOWN_SEVERITY_ORDER
from humansays.enums import Disposition, Severity, SignalName
from humansays.findings.models import Finding
from humansays.reporting.models import FileReport


class RuleView(TypedDict):
    """``RuleSpec`` as it appears in output, field for field."""

    signal: SignalName
    severity: Severity
    confidence: float
    weight: float
    review_question: str
    disposition: Disposition


class ObservationView(TypedDict):
    """``Observation`` as it appears in output, field for field."""

    message: str
    evidence: tuple[str, ...]


class Signal(TypedDict):
    """One rule firing against one symbol.

    ``rule_id`` is carried separately because it is a ``RuleSpec`` property
    rather than a field, so ``asdict`` does not produce it.
    """

    rule_id: str
    rule: RuleView
    observation: ObservationView


class Target(TypedDict):
    """One symbol in one file, with every signal that fired against it."""

    path: str
    symbol: str
    line: int
    end_line: int
    signals: list[Signal]


def signal_sort_key(signal: Signal) -> tuple[int, str]:
    order = SEVERITY_ORDER.get(signal['rule']['severity'], UNKNOWN_SEVERITY_ORDER)
    return (order, signal['rule_id'])


def target_sort_key(target: Target) -> tuple[int, int, str, int]:
    best = min(
        SEVERITY_ORDER.get(signal['rule']['severity'], UNKNOWN_SEVERITY_ORDER)
        for signal in target['signals']
    )
    return (best, -len(target['signals']), target['path'], target['line'])


def create_review_target(report: FileReport, symbol: str, line: int) -> Target:
    return {
        'path': str(report.path),
        'symbol': symbol,
        'line': line,
        'end_line': line,
        'signals': [],
    }


def create_signal(finding: Finding) -> Signal:
    # asdict() is untyped, so the casts are unchecked: RuleView and
    # ObservationView have to be edited whenever RuleSpec or Observation
    # gains or loses a field.
    return {
        'rule_id': finding.rule.rule_id,
        'rule': cast('RuleView', dataclasses.asdict(finding.rule)),
        'observation': cast('ObservationView', dataclasses.asdict(finding.observation)),
    }


def is_shown(finding: Finding, *, show_evidence: bool) -> bool:
    """Whether a finding appears in output at all.

    Evidence is collected and scored like anything else -- it is withheld from
    display, not from the pipeline -- so the filter lives here, at the one seam
    both renderers pass through, rather than in `evaluate`. Removing it earlier
    would make it unavailable to the flag that exists to show it.
    """
    return show_evidence or finding.rule.disposition is not Disposition.EVIDENCE


def review_targets(reports: list[FileReport], *, show_evidence: bool) -> list[Target]:
    grouped: dict[tuple[str, str], Target] = {}
    for report in reports:
        for finding in report.findings:
            if not is_shown(finding, show_evidence=show_evidence):
                continue

            location = finding.location
            key = (str(report.path), location.symbol)
            if key not in grouped:
                symbol = location.symbol
                grouped[key] = create_review_target(report, symbol, location.line)

            target = grouped[key]
            target['line'] = min(target['line'], location.line)
            target['end_line'] = max(target['end_line'], location.end_line)
            target['signals'].append(create_signal(finding))

    targets = list(grouped.values())
    for target in targets:
        target['signals'].sort(key=signal_sort_key)

    targets.sort(key=target_sort_key)
    return targets


def shown_targets(targets: list[Target], limit: int) -> list[Target]:
    return targets if limit == 0 else targets[:limit]
