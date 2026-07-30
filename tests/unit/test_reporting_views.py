"""The output views and the dataclasses they mirror carry the same fields.

`create_signal` builds the JSON payload with `dataclasses.asdict` and casts the
result to a `TypedDict`. A cast is unchecked, so `RuleView` and
`ObservationView` do not constrain what `asdict` produces -- they only describe
what the author believed it produced. The comment at
`reporting/grouping.py:79-81` states the obligation to edit them together, and
until this file existed nothing held anyone to it.

The failure mode is quiet in both directions. A field added to `RuleSpec`
appears in every JSON signal object whether or not `RuleView` mentions it, so
the schema moves with no diff in the reporting layer at all. A field removed
leaves `RuleView` advertising a key that consumers will not find.
"""

from __future__ import annotations

import dataclasses

from humansays.findings.models import Observation, RuleSpec
from humansays.reporting.grouping import ObservationView, RuleView


def field_names(dataclass: type) -> set[str]:
    return {field.name for field in dataclasses.fields(dataclass)}


def test_rule_view_matches_rule_spec() -> None:
    assert set(RuleView.__annotations__) == field_names(RuleSpec)


def test_observation_view_matches_observation() -> None:
    assert set(ObservationView.__annotations__) == field_names(Observation)
