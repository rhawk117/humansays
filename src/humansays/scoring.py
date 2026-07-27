"""Scoring.

The score answers one question: how much signal is there per unit of code?
Each finding contributes ``weight * confidence``; the total is expressed per 100
lines as ``density``, and the score is ``100 / (1 + density / tolerance)`` so it
decays smoothly and never leaves the 0-100 range. A file with no weighted
findings scores 100. ``SCORE_TOLERANCE`` is calibrated so that roughly one
warning per 100 lines lands in the mid-seventies.

Density rather than a raw count means a large clean module is not punished for
its size, and a small module full of warnings cannot hide behind a low total.
"""

from .const import GRADE_BANDS, PERFECT_SCORE, SCORE_TOLERANCE, SCORE_WINDOW
from .enums import Grade
from .findings.models import Score
from .reporting.models import ScanResult


def grade_for(value: float) -> Grade:
    for floor, grade in GRADE_BANDS:
        if value >= floor:
            return grade
    return Grade.F


def score_for(result: ScanResult) -> Score:
    penalty = sum(finding.rule.penalty for finding in result.findings)
    lines = max(1, result.lines)
    density = penalty * SCORE_WINDOW / lines
    value = round(PERFECT_SCORE / (1.0 + density / SCORE_TOLERANCE), 1)
    return Score(
        lines=lines,
        value=value,
        penalty=round(penalty, 2),
        density=round(density, 3),
        grade=grade_for(value),
    )
