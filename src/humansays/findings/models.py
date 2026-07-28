"""Finding models.

Frozen dataclasses carrying anything that can come from a rule evaluation:
a rule's identity and severity, where it fired, and what it observed.
Validation happens in ``__post_init__`` so a malformed ``RuleSpec`` fails at
construction time with a real error message, same as the pydantic models this
replaces.
"""

from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from humansays.enums import Grade, Severity, SignalName

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


def check_bounds(pairs: tuple[tuple[float, float, float | None, str], ...]) -> None:
    for value, low, high, name in pairs:
        if value < low or (high is not None and value > high):
            raise ValueError(f'{name} out of range [{low},{high}]: {value}')


def field_values(instance: 'DataclassInstance') -> dict:
    """A dataclass's fields, one level deep."""
    return {field.name: getattr(instance, field.name) for field in fields(instance)}


@dataclass(frozen=True, slots=True)
class Location:
    symbol: str
    line: int
    end_line: int


@dataclass(frozen=True, slots=True)
class Observation:
    message: str
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Incident:
    line: int
    detail: str


@dataclass(frozen=True, slots=True)
class RuleSpec:
    signal: SignalName
    severity: Severity
    confidence: float
    weight: float
    review_question: str

    def __post_init__(self) -> None:
        check_bounds((
            (self.confidence, 0.0, 1.0, 'confidence'),
            (self.weight, 0.0, None, 'weight'),
        ))

    @property
    def rule_id(self) -> str:
        return self.signal.name

    @property
    def penalty(self) -> float:
        return self.weight * self.confidence


@dataclass(frozen=True, slots=True)
class Score:
    lines: int
    penalty: float
    density: float
    value: float
    grade: Grade


@dataclass(frozen=True, slots=True)
class Finding:
    rule: RuleSpec
    location: Location
    observation: Observation

    @property
    def sort_key(self) -> tuple[int, str]:
        return (self.location.line, self.rule.rule_id)
