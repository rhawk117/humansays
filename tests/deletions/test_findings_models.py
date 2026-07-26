import pytest
from humansays.findings.models import RuleSpec

from humansays.enums import Severity, SignalName


def test_rulespec_rejects_confidence_above_one() -> None:
    with pytest.raises(ValueError, match='confidence'):
        RuleSpec(
            SignalName.HS001,
            Severity.WARNING,
            confidence=1.5,
            weight=3.0,
            review_question='q',
        )


def test_rulespec_penalty_is_weight_times_confidence() -> None:
    spec = RuleSpec(
        SignalName.HS001,
        Severity.WARNING,
        confidence=0.8,
        weight=3.0,
        review_question='q',
    )
    assert spec.penalty == pytest.approx(2.4)
