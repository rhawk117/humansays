"""HS017, HS009, HS022, HS003 and HS019: how much a reader holds at once."""

from humansays.config.models import Thresholds
from humansays.enums import SignalName
from humansays.facts.module import ModuleFacts
from humansays.facts.values import FunctionFacts
from humansays.findings.models import Location
from humansays.rules.models import Emission


def module_scale(facts: ModuleFacts, thresholds: Thresholds) -> list[Emission]:
    count = facts.line_count
    limit = thresholds.modules.max_lines
    if count <= limit:
        return []

    return [
        Emission(
            SignalName.HS017,
            Location('<module>', 1, max(1, count)),
            (f'configured threshold: {limit}',),
            payload={'count': count},
        ),
    ]


def function_scale(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    limits = thresholds.functions
    emissions: list[Emission] = []
    if facts.length > limits.max_lines:
        emissions.append(
            Emission(
                SignalName.HS009,
                facts.location,
                (f'configured threshold: {limits.max_lines}',),
                payload={'count': facts.length},
            ),
        )

    if facts.body.code_lines > limits.max_code_lines:
        emissions.append(
            Emission(
                SignalName.HS022,
                facts.location,
                (
                    f'configured threshold: {limits.max_code_lines}',
                    'blank lines, comments, and the docstring are excluded',
                ),
                payload={'count': facts.body.code_lines},
            ),
        )

    return emissions


def control_flow(facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]:
    limits = thresholds.functions
    emissions: list[Emission] = []
    limit = limits.nesting_limit(facts.class_name)
    if facts.body.maximum_nesting > limit:
        evidence = [f'configured threshold: {limit}']
        if facts.class_name:
            evidence.append(
                f'class bodies receive +{limits.class_nesting_bonus} nesting',
            )

        emissions.append(
            Emission(
                SignalName.HS003,
                facts.location,
                tuple(evidence),
                payload={'depth': facts.body.maximum_nesting},
            ),
        )

    if facts.body.branches > limits.max_branches:
        emissions.append(
            Emission(
                SignalName.HS019,
                facts.location,
                (f'configured threshold: {limits.max_branches}',),
                payload={'count': facts.body.branches},
            ),
        )

    return emissions
