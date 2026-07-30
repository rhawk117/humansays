"""In-memory shape of one rule definition.

``RuleDefinition`` wraps a :class:`RuleSpec` rather than extending it.
``RuleSpec`` is serialized field-for-field into the JSON report
(``reporting/grouping.py``), so a field added there becomes a key in every
emitted signal object. The message template belongs to the rules layer alone
and stays outside the spec.
"""

from collections.abc import Mapping
from dataclasses import dataclass

from humansays.findings.models import RuleSpec


@dataclass(frozen=True, slots=True)
class RuleDefinition:
    spec: RuleSpec
    message: str
    placeholders: frozenset[str]

    def render(self, payload: Mapping[str, object]) -> str:
        """Format ``message`` from ``payload``, rejecting any mismatch.

        ``str.format`` ignores surplus keyword arguments, so an adapter that
        stops supplying a value renders a template with a stale placeholder
        left unfilled rather than failing. The equality check is what turns
        that into an error.
        """
        if payload.keys() != self.placeholders:
            raise ValueError(
                f'{self.spec.rule_id}: payload keys {sorted(payload)} do not match '
                f'placeholders {sorted(self.placeholders)}'
            )

        return self.message.format(**payload)
