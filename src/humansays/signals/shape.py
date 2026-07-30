"""HS009, HS022, HS003 and HS019: how large a function is and how it branches."""

from humansays.config.models import FunctionThresholds
from humansays.enums import SignalName
from humansays.facts.values import FunctionFacts
from humansays.rules.models import Emission


def size_signals(facts: FunctionFacts, limits: FunctionThresholds) -> list[Emission]:
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


def control_flow_signals(
    facts: FunctionFacts,
    limits: FunctionThresholds,
) -> list[Emission]:
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
