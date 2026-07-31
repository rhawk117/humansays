"""Evidence is withheld from display, not from the pipeline.

**No shipped rule has the `evidence` disposition.** Phase C2 built the
mechanism and demoted only the three `hint` rules; the ten rules the
reconciliation maps to `evidence` are C3's work. So everything here runs
against a synthetic `RuleSpec` built in the test rather than against a loaded
`rules.toml`, and that is a real limitation: if a shipped evidence rule would
be defined differently from this fixture, nothing here would notice.

What this does establish is that the filter is at the seam both renderers pass
through, and that the finding survives long enough to be shown when asked for.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from humansays.enums import Disposition, Severity, SignalName
from humansays.findings.models import Finding, Location, Observation, RuleSpec
from humansays.reporting.grouping import is_shown, review_targets
from humansays.reporting.models import FileReport


def spec_with(disposition: Disposition) -> RuleSpec:
    return RuleSpec(
        signal=SignalName.HS017,
        severity=Severity.WARNING,
        confidence=0.6,
        weight=3.0,
        review_question='q',
        disposition=disposition,
    )


def finding_with(disposition: Disposition) -> Finding:
    return Finding(
        rule=spec_with(disposition),
        location=Location('<module>', 1, 1),
        observation=Observation('Module spans 600 source lines.', ()),
    )


SHOWN_BY_DEFAULT = {
    Disposition.ON: True,
    Disposition.HINT: True,
    Disposition.EVIDENCE: False,
}


@pytest.mark.parametrize('disposition', sorted(SHOWN_BY_DEFAULT))
def test_only_evidence_is_withheld_by_default(disposition: Disposition) -> None:
    finding = finding_with(disposition)
    assert is_shown(finding, show_evidence=False) is SHOWN_BY_DEFAULT[disposition]
    assert is_shown(finding, show_evidence=True) is True


def test_every_displayable_disposition_is_covered() -> None:
    """OFF is absent because an OFF rule never reaches display to be filtered.

    That short-circuit is `is_emitted` in `rules/registry.py`, and the test
    that holds it is
    `test_cli_contract.py::test_off_is_not_emitted_even_with_show_evidence`.
    Until phase C2's closeout that sentence was this file's own justification
    for the exclusion and nothing implemented it, so an OFF finding was in
    fact emitted and shown.
    """
    assert set(SHOWN_BY_DEFAULT) == set(Disposition) - {Disposition.OFF}


def report_for(disposition: Disposition) -> FileReport:
    return FileReport(Path('module.py'), 10, 0, 0, set(), [finding_with(disposition)])


def test_evidence_is_absent_from_targets_until_asked_for() -> None:
    reports = [report_for(Disposition.EVIDENCE)]
    assert review_targets(reports, show_evidence=False) == []

    shown = review_targets(reports, show_evidence=True)
    assert [signal['rule_id'] for target in shown for signal in target['signals']] == [
        'HS017'
    ]


def test_a_scored_finding_is_unaffected_by_the_flag() -> None:
    """The flag adds evidence; it does not otherwise change the report."""
    reports = [report_for(Disposition.ON)]
    assert review_targets(reports, show_evidence=False) == review_targets(
        reports, show_evidence=True
    )
