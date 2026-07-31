"""Disposition decides whether a finding is scored; severity decides how much.

This is the enforcer the phase C2 plan names for its invariant 3 -- *a `hint`
or `evidence` finding contributes zero penalty*. The filter itself lives on
``RuleSpec.penalty`` rather than in ``scoring.py``, so it is single-sourced at
the definition of penalty instead of at one of its callers; the assertions here
run through ``score_for`` anyway, because the invariant is about the score a
caller sees, not about the property it happens to be implemented on.

Every rule is built here rather than loaded from a shipped ``rules.toml``.
``evidence`` and ``off`` have no shipped instance after C2, so a test that
drew its inputs from the real definitions could not reach two of the four
dispositions at all.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from humansays.enums import Disposition, Grade, Severity, SignalName
from humansays.findings.models import Finding, Location, Observation, RuleSpec
from humansays.reporting.models import FileReport, ScanResult
from humansays.scoring import score_for

WEIGHT = 3.0
CONFIDENCE = 0.5
PENALTY = WEIGHT * CONFIDENCE

SCORES = {
    Disposition.ON: PENALTY,
    Disposition.HINT: 0.0,
    Disposition.EVIDENCE: 0.0,
    Disposition.OFF: 0.0,
}


def finding_with(disposition: Disposition) -> Finding:
    spec = RuleSpec(
        signal=SignalName.HS017,
        severity=Severity.WARNING,
        confidence=CONFIDENCE,
        weight=WEIGHT,
        review_question='q',
        disposition=disposition,
    )
    return Finding(spec, Location('<module>', 1, 1), Observation('observed.', ()))


def result_with(*findings: Finding, lines: int = 100) -> ScanResult:
    report = FileReport(Path('module.py'), lines, 0, 0, set(), list(findings))
    return ScanResult('<test>', [report], [])


@pytest.mark.parametrize('disposition', sorted(SCORES))
def test_only_an_on_rule_contributes_penalty(disposition: Disposition) -> None:
    score = score_for(result_with(finding_with(disposition)))
    assert score.penalty == pytest.approx(SCORES[disposition])


def test_every_disposition_is_covered() -> None:
    """A disposition added without a scoring decision fails here, not silently."""
    assert set(SCORES) == set(Disposition)


def test_an_unscored_finding_leaves_a_perfect_score() -> None:
    """Findings are still reported; the score is what disposition withholds."""
    result = result_with(finding_with(Disposition.HINT))
    score = score_for(result)
    assert score.value == 100.0
    assert score.grade == Grade.A
    assert len(result.findings) == 1


def test_severity_still_governs_the_amount_once_a_rule_scores() -> None:
    """Disposition gates scoring; it does not replace the weight."""
    heavy = finding_with(Disposition.ON)
    light = Finding(
        RuleSpec(
            signal=SignalName.HS017,
            severity=Severity.ADVISORY,
            confidence=CONFIDENCE,
            weight=1.0,
            review_question='q',
            disposition=Disposition.ON,
        ),
        Location('<module>', 1, 1),
        Observation('observed.', ()),
    )
    assert score_for(result_with(heavy)).penalty > score_for(result_with(light)).penalty
