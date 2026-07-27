"""Per-rule detection tests: one class per rule, positive case then negative."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import TYPE_CHECKING

from humansays.analysis.models import ParsedModule
from humansays.analysis.rules import RulesetEvaluator
from humansays.config.models import Thresholds
from humansays.enums import Severity, SignalName
from tests.fixtures import sources

if TYPE_CHECKING:
    from humansays.findings.models import Finding


def analyze(source: str, thresholds: Thresholds | None = None) -> list[Finding]:
    module = ParsedModule(Path('<snippet>'), source, ast.parse(source))
    return RulesetEvaluator(module, thresholds or Thresholds()).run()


def signals(findings: list[Finding]) -> list[SignalName]:
    return [finding.rule.signal for finding in findings]


def findings_for(findings: list[Finding], signal: SignalName) -> list[Finding]:
    return [finding for finding in findings if finding.rule.signal is signal]


class TestStaticMethodRule:
    def test_staticmethod_is_reported(self) -> None:
        found = findings_for(analyze(sources.STATIC_METHOD), SignalName.HS015)
        assert len(found) == 1
        assert found[0].location.symbol == 'Router.classify'
        assert found[0].rule.severity is Severity.WARNING

    def test_classmethod_and_module_function_are_not_reported(self) -> None:
        found = analyze(sources.CLASSMETHOD_AND_FUNCTION)
        assert SignalName.HS015 not in signals(found)


class TestLambdaRule:
    def test_lambda_is_reported_in_every_scope(self) -> None:
        found = findings_for(analyze(sources.LAMBDAS_IN_THREE_SCOPES), SignalName.HS016)
        symbols = sorted(finding.location.symbol for finding in found)
        assert symbols == ['<module>', 'Holder.pick', 'sort_items']

    def test_named_function_is_not_reported(self) -> None:
        assert SignalName.HS016 not in signals(analyze(sources.NAMED_FUNCTION))


class TestLazyImportRule:
    def test_imports_inside_a_function_are_reported(self) -> None:
        found = findings_for(analyze(sources.LAZY_IMPORT), SignalName.HS021)
        assert len(found) == 2
        assert all(item.location.symbol == 'render' for item in found)

    def test_module_level_imports_are_not_reported(self) -> None:
        found = analyze(sources.MODULE_LEVEL_IMPORT)
        assert SignalName.HS021 not in signals(found)


class TestModuleLengthRule:
    def test_long_file_is_reported(self) -> None:
        found = findings_for(analyze(sources.line_padding(600)), SignalName.HS017)
        assert len(found) == 1
        assert '600 source lines' in found[0].observation.message

    def test_file_at_threshold_is_not_reported(self) -> None:
        found = analyze(sources.line_padding(500))
        assert SignalName.HS017 not in signals(found)


class TestFunctionSizeRule:
    def test_blank_lines_count_toward_span_but_not_code(self) -> None:
        found = signals(analyze(sources.padded_function(30, 30)))
        assert SignalName.HS009 in found
        assert SignalName.HS022 not in found

    def test_dense_function_trips_the_code_line_rule(self) -> None:
        found = findings_for(analyze(sources.padded_function(70, 0)), SignalName.HS022)
        assert len(found) == 1
        assert '72 lines of code' in found[0].observation.message


class TestBaseClassRule:
    def test_multiple_inheritance_is_reported(self) -> None:
        found = findings_for(analyze(sources.MULTIPLE_INHERITANCE), SignalName.HS018)
        assert len(found) == 1
        assert found[0].observation.evidence == ('Reader', 'Writer')

    def test_single_inheritance_is_not_reported(self) -> None:
        found = analyze(sources.SINGLE_INHERITANCE)
        assert SignalName.HS018 not in signals(found)


class TestBranchRule:
    def test_branch_count_includes_elif(self) -> None:
        found = findings_for(analyze(sources.branch_chain(6)), SignalName.HS019)
        assert len(found) == 1
        assert '6 if/elif statements' in found[0].observation.message

    def test_branches_at_threshold_are_not_reported(self) -> None:
        found = analyze(sources.branch_chain(5))
        assert SignalName.HS019 not in signals(found)


class TestNestingRule:
    def test_module_function_uses_base_limit(self) -> None:
        found = findings_for(analyze(sources.NESTED_LOOPS), SignalName.HS003)
        assert len(found) == 1

    def test_method_receives_the_class_bonus(self) -> None:
        found = analyze(sources.NESTED_LOOPS_IN_METHOD)
        assert SignalName.HS003 not in signals(found)

    def test_method_one_level_deeper_still_fires(self) -> None:
        found = analyze(sources.NESTED_LOOPS_IN_METHOD_DEEPER)
        assert SignalName.HS003 in signals(found)


class TestScoringWeights:
    def test_documentation_notices_do_not_cost_points(self) -> None:
        findings = analyze(sources.NAMED_FUNCTION)
        assert all(finding.rule.weight == 0.0 for finding in findings)


class TestSmellyFixture:
    def test_fixture_reports_every_new_rule(self) -> None:
        reported = set(signals(analyze(sources.SMELLY_MODULE)))
        expected = {
            SignalName.HS015,
            SignalName.HS016,
            SignalName.HS018,
            SignalName.HS019,
            SignalName.HS021,
        }
        assert expected <= reported
