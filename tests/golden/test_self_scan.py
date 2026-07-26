"""Self-scan gate: humansays scanning its own source.

The gate is exact-match, not a ceiling: every weighted finding humansays
reports against its own source must be listed in ``self-scan-baseline.json``
with a reason, and every baseline entry must still be reproduced. A finding
that stops showing up means the baseline has gone stale and must be pruned,
not silently carried forward.
"""

import json
from pathlib import Path

from humansays import application
from humansays.config.models import ScannerSettings, Selection

BASELINE_PATH = Path(__file__).parent / 'self-scan-baseline.json'
SRC_ROOT = 'src/humansays'


def _current_weighted_findings() -> set[tuple[str, str, int, str, str]]:
    settings = ScannerSettings(selection=Selection(paths=(SRC_ROOT,)))
    paths = application.collect_files([SRC_ROOT], settings.selection.excludes)
    result = application.analyze_paths(paths, settings)
    assert not result.errors, f'self-scan hit parse errors: {result.errors}'
    return {
        (
            str(report.path),
            finding.location.symbol,
            finding.location.line,
            finding.rule.rule_id,
            evidence,
        )
        for report in result.reports
        for finding in report.findings
        if finding.rule.weight > 0
        for evidence in (finding.observation.evidence or ('',))
    }


def _baseline_findings() -> set[tuple[str, str, int, str, str]]:
    entries = json.loads(BASELINE_PATH.read_text(encoding='utf-8'))['entries']
    return {
        (
            entry['path'],
            entry['symbol'],
            entry['line'],
            entry['rule_id'],
            entry['evidence'],
        )
        for entry in entries
    }


def test_self_scan_matches_baseline_exactly() -> None:
    current = _current_weighted_findings()
    baseline = _baseline_findings()

    unexplained = current - baseline
    assert not unexplained, (
        f'New weighted self-scan findings with no baseline entry: {unexplained}'
    )

    stale = baseline - current
    assert not stale, f'Baseline entries no longer reproduced (prune them): {stale}'
