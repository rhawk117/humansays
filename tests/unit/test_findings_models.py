import pytest

from humansays.enums import Disposition, Severity, SignalName
from humansays.findings.models import RuleSpec


def test_rulespec_rejects_confidence_above_one() -> None:
    with pytest.raises(ValueError, match='confidence'):
        RuleSpec(
            SignalName.HS001,
            Severity.WARNING,
            confidence=1.5,
            weight=3.0,
            review_question='q',
            disposition=Disposition.ON,
        )


def test_rulespec_penalty_is_weight_times_confidence() -> None:
    spec = RuleSpec(
        SignalName.HS001,
        Severity.WARNING,
        confidence=0.8,
        weight=3.0,
        review_question='q',
        disposition=Disposition.ON,
    )
    assert spec.penalty == pytest.approx(2.4)


@pytest.mark.parametrize(
    'disposition', [Disposition.HINT, Disposition.EVIDENCE, Disposition.OFF]
)
def test_rulespec_outside_on_contributes_no_penalty(disposition: Disposition) -> None:
    """Weight and confidence are unchanged; only the contribution is dropped.

    Zeroing the weight in the data instead would lose the calibration, and it
    would make a demotion indistinguishable in JSON from a rule someone had
    decided was worthless.
    """
    spec = RuleSpec(
        SignalName.HS001,
        Severity.WARNING,
        confidence=0.8,
        weight=3.0,
        review_question='q',
        disposition=disposition,
    )
    assert spec.penalty == 0.0
    assert spec.weight == 3.0
    assert spec.confidence == pytest.approx(0.8)
