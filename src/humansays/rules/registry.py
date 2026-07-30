"""Turning what a rule measured into a finding.

Rule metadata is reached through :func:`rule_definitions`, which is keyed by
:class:`SignalName`, so a rule id is never a loose string:
``rule_definitions()[SignalName.HS015]`` is the only way to reach a spec, and a
typo is an immediate ``KeyError`` rather than a silently missing finding.
"""

from humansays.findings.models import Finding, Observation
from humansays.rules.loading import rule_definitions
from humansays.rules.models import Emission


def build_finding(emission: Emission) -> Finding:
    """The single construction site: definition plus measurement."""
    definition = rule_definitions()[emission.signal]
    return Finding(
        definition.spec,
        emission.location,
        Observation(definition.render(emission.payload), emission.evidence),
    )
