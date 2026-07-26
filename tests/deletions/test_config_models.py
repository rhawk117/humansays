import pytest

from humansays.config.models import FunctionThresholds, Report


def test_max_lines_must_be_at_least_one() -> None:
    with pytest.raises(ValueError, match='max_lines'):
        FunctionThresholds(max_lines=0)


def test_min_score_bounds() -> None:
    with pytest.raises(ValueError, match='min_score'):
        Report(min_score=101.0)


def test_defaults_match_poc() -> None:
    thresholds = FunctionThresholds()
    assert (
        thresholds.max_arguments,
        thresholds.max_nesting,
        thresholds.max_branches,
        thresholds.max_lines,
        thresholds.max_code_lines,
    ) == (3, 3, 5, 50, 65)
