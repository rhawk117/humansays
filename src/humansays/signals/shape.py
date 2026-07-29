"""HS009, HS022, HS003 and HS019: how large a function is and how it branches."""

from humansays.catalog import build_finding
from humansays.config.models import FunctionThresholds
from humansays.enums import SignalName
from humansays.facts.values import FunctionFacts
from humansays.findings.models import Finding, Observation


def size_signals(facts: FunctionFacts, limits: FunctionThresholds) -> list[Finding]:
    findings: list[Finding] = []
    if facts.length > limits.max_lines:
        findings.append(
            build_finding(
                SignalName.HS009,
                facts.location,
                Observation(
                    f'Function spans {facts.length} source lines.',
                    (f'configured threshold: {limits.max_lines}',),
                ),
            ),
        )

    if facts.body.code_lines > limits.max_code_lines:
        findings.append(
            build_finding(
                SignalName.HS022,
                facts.location,
                Observation(
                    f'Function holds {facts.body.code_lines} lines of code.',
                    (
                        f'configured threshold: {limits.max_code_lines}',
                        'blank lines, comments, and the docstring are excluded',
                    ),
                ),
            ),
        )

    return findings


def control_flow_signals(
    facts: FunctionFacts,
    limits: FunctionThresholds,
) -> list[Finding]:
    findings: list[Finding] = []
    limit = limits.nesting_limit(facts.class_name)
    if facts.body.maximum_nesting > limit:
        evidence = [f'configured threshold: {limit}']
        if facts.class_name:
            evidence.append(
                f'class bodies receive +{limits.class_nesting_bonus} nesting',
            )

        findings.append(
            build_finding(
                SignalName.HS003,
                facts.location,
                Observation(
                    f'Control flow reaches nesting depth {facts.body.maximum_nesting}.',
                    tuple(evidence),
                ),
            ),
        )

    if facts.body.branches > limits.max_branches:
        findings.append(
            build_finding(
                SignalName.HS019,
                facts.location,
                Observation(
                    f'Function contains {facts.body.branches} if/elif statements.',
                    (f'configured threshold: {limits.max_branches}',),
                ),
            ),
        )

    return findings
