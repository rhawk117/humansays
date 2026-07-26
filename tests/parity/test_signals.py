"""Tests for the structural signal scanner, including a scan of its own source."""

import ast
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import poc_fixtures as fixtures

from humansays.analysis.models import ParsedModule
from humansays.analysis.rules import Analyzer
from humansays.cli import main
from humansays.config.models import Thresholds
from humansays.enums import Grade, Severity, SignalName
from humansays.findings.models import Finding

PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent / 'src' / 'humansays'
BASELINE_PATH = (
    Path(__file__).resolve().parent.parent / 'golden' / 'self-scan-baseline.json'
)
BANNED_SIGNALS = frozenset({SignalName.HS015, SignalName.HS016})
NOTICE_SIGNALS = frozenset()


def _baselined_signals() -> frozenset[SignalName]:
    entries = json.loads(BASELINE_PATH.read_text(encoding='utf-8'))['entries']
    return frozenset(SignalName[entry['rule_id']] for entry in entries)


def analyze(source: str, thresholds: Thresholds | None = None) -> list[Finding]:
    module = ParsedModule(Path('<snippet>'), source, ast.parse(source))
    return Analyzer(module, thresholds or Thresholds()).run()


def signals(findings: list[Finding]) -> list[SignalName]:
    return [finding.rule.signal for finding in findings]


def findings_for(findings: list[Finding], signal: SignalName) -> list[Finding]:
    return [finding for finding in findings if finding.rule.signal is signal]


def run_cli(argv: list[str], piped: str = '') -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(io.StringIO()):
        code = main(argv, io.StringIO(piped))
    return code, buffer.getvalue()


class StaticMethodRuleTests(unittest.TestCase):
    def test_staticmethod_is_reported(self) -> None:
        found = findings_for(analyze(fixtures.STATIC_METHOD), SignalName.HS015)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].location.symbol, 'Router.classify')
        self.assertIs(found[0].rule.severity, Severity.WARNING)

    def test_classmethod_and_module_function_are_not_reported(self) -> None:
        found = analyze(fixtures.CLASSMETHOD_AND_FUNCTION)
        self.assertNotIn(SignalName.HS015, signals(found))


class LambdaRuleTests(unittest.TestCase):
    def test_lambda_is_reported_in_every_scope(self) -> None:
        found = findings_for(analyze(fixtures.LAMBDAS_IN_THREE_SCOPES), SignalName.HS016)
        symbols = sorted(finding.location.symbol for finding in found)
        self.assertEqual(symbols, ['<module>', 'Holder.pick', 'sort_items'])

    def test_named_function_is_not_reported(self) -> None:
        self.assertNotIn(SignalName.HS016, signals(analyze(fixtures.NAMED_FUNCTION)))


class LazyImportRuleTests(unittest.TestCase):
    def test_imports_inside_a_function_are_reported(self) -> None:
        found = findings_for(analyze(fixtures.LAZY_IMPORT), SignalName.HS021)
        self.assertEqual(len(found), 2)
        self.assertTrue(all(item.location.symbol == 'render' for item in found))

    def test_module_level_imports_are_not_reported(self) -> None:
        found = analyze(fixtures.MODULE_LEVEL_IMPORT)
        self.assertNotIn(SignalName.HS021, signals(found))


class ModuleLengthRuleTests(unittest.TestCase):
    def test_long_file_is_reported(self) -> None:
        found = findings_for(analyze(fixtures.line_padding(600)), SignalName.HS017)
        self.assertEqual(len(found), 1)
        self.assertIn('600 source lines', found[0].observation.message)

    def test_file_at_threshold_is_not_reported(self) -> None:
        found = analyze(fixtures.line_padding(500))
        self.assertNotIn(SignalName.HS017, signals(found))


class FunctionSizeRuleTests(unittest.TestCase):
    def test_blank_lines_count_toward_span_but_not_code(self) -> None:
        found = signals(analyze(fixtures.padded_function(30, 30)))
        self.assertIn(SignalName.HS009, found)
        self.assertNotIn(SignalName.HS022, found)

    def test_dense_function_trips_the_code_line_rule(self) -> None:
        found = findings_for(analyze(fixtures.padded_function(70, 0)), SignalName.HS022)
        self.assertEqual(len(found), 1)
        self.assertIn('72 lines of code', found[0].observation.message)


class BaseClassRuleTests(unittest.TestCase):
    def test_multiple_inheritance_is_reported(self) -> None:
        found = findings_for(analyze(fixtures.MULTIPLE_INHERITANCE), SignalName.HS018)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].observation.evidence, ('Reader', 'Writer'))

    def test_single_inheritance_is_not_reported(self) -> None:
        found = analyze(fixtures.SINGLE_INHERITANCE)
        self.assertNotIn(SignalName.HS018, signals(found))


class BranchRuleTests(unittest.TestCase):
    def test_branch_count_includes_elif(self) -> None:
        found = findings_for(analyze(fixtures.branch_chain(6)), SignalName.HS019)
        self.assertEqual(len(found), 1)
        self.assertIn('6 if/elif statements', found[0].observation.message)

    def test_branches_at_threshold_are_not_reported(self) -> None:
        found = analyze(fixtures.branch_chain(5))
        self.assertNotIn(SignalName.HS019, signals(found))


class NestingRuleTests(unittest.TestCase):
    def test_module_function_uses_base_limit(self) -> None:
        found = findings_for(analyze(fixtures.NESTED_LOOPS), SignalName.HS003)
        self.assertEqual(len(found), 1)

    def test_method_receives_the_class_bonus(self) -> None:
        found = analyze(fixtures.NESTED_LOOPS_IN_METHOD)
        self.assertNotIn(SignalName.HS003, signals(found))

    def test_method_one_level_deeper_still_fires(self) -> None:
        found = analyze(fixtures.NESTED_LOOPS_IN_METHOD_DEEPER)
        self.assertIn(SignalName.HS003, signals(found))


class ScoringTests(unittest.TestCase):
    def test_documentation_notices_do_not_cost_points(self) -> None:
        findings = analyze(fixtures.NAMED_FUNCTION)
        self.assertTrue(all(finding.rule.weight == 0.0 for finding in findings))

    def test_clean_source_scores_an_a(self) -> None:
        _, output = run_cli([str(PACKAGE_ROOT), '--format', 'json'])
        score = json.loads(output)['score']
        self.assertEqual(score['grade'], Grade.A)

    def test_smelly_source_scores_badly(self) -> None:
        _, output = run_cli(['--format', 'json'], str(fixtures.FIXTURE_MODULE_PATH))
        score = json.loads(output)['score']
        self.assertLess(score['value'], 60.0)
        self.assertGreater(score['penalty'], 0.0)

    def test_min_score_gates_the_exit_code(self) -> None:
        code, _ = run_cli(
            ['--min-score', '90'],
            str(fixtures.FIXTURE_MODULE_PATH),
        )
        self.assertEqual(code, 1)


class ConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        handle = tempfile.NamedTemporaryFile(
            'w',
            suffix='.toml',
            delete=False,
            encoding='utf-8',
        )
        handle.write(fixtures.CONFIG_TOML)
        handle.close()
        self.config = handle.name
        self.addCleanup(Path(self.config).unlink)

    def test_toml_thresholds_are_applied(self) -> None:
        code, output = run_cli(
            ['--config', self.config, '--format', 'json', '--min-score', '0'],
            str(fixtures.FIXTURE_MODULE_PATH),
        )
        payload = json.loads(output)
        indicators = {
            signal['rule_id']
            for target in payload['targets']
            for signal in target['signals']
        }
        self.assertEqual(code, 0)
        self.assertIn('HS017', indicators)

    def test_command_line_overrides_the_file(self) -> None:
        code, output = run_cli(
            [
                '--config',
                self.config,
                '--format',
                'json',
                '--max-file-lines',
                '5000',
                '--min-score',
                '0',
            ],
            str(fixtures.FIXTURE_MODULE_PATH),
        )
        payload = json.loads(output)
        indicators = {
            signal['rule_id']
            for target in payload['targets']
            for signal in target['signals']
        }
        self.assertEqual(code, 0)
        self.assertNotIn('HS017', indicators)

    def test_file_min_score_can_fail_the_run(self) -> None:
        code, _ = run_cli(
            ['--config', self.config],
            str(fixtures.FIXTURE_MODULE_PATH),
        )
        self.assertEqual(code, 1)


class InputResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = str(fixtures.FIXTURE_MODULE_PATH)

    def test_paths_can_be_piped_on_stdin(self) -> None:
        code, output = run_cli(['--format', 'json'], f'{self.fixture}\n')
        payload = json.loads(output)
        self.assertEqual(code, 0)
        self.assertEqual(payload['summary']['files'], 1)
        self.assertEqual(payload['root'], '<stdin>')

    def test_nul_separated_paths_are_accepted(self) -> None:
        code, output = run_cli(['-', '--format', 'json'], f'{self.fixture}\0')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)['summary']['files'], 1)

    def test_fail_on_warning_sets_exit_code(self) -> None:
        code, _ = run_cli(['-', '--fail-on', 'warning'], f'{self.fixture}\n')
        self.assertEqual(code, 1)

    def test_fail_on_never_is_the_default(self) -> None:
        code, _ = run_cli(['-'], f'{self.fixture}\n')
        self.assertEqual(code, 0)

    def test_missing_paths_exit_three(self) -> None:
        code, _ = run_cli(['-'], '/nonexistent/path.py\n')
        self.assertEqual(code, 3)

    def test_unknown_symbol_exits_two(self) -> None:
        code, _ = run_cli(['-', '--symbol', 'nope'], f'{self.fixture}\n')
        self.assertEqual(code, 2)

    def test_symbol_filter_narrows_targets(self) -> None:
        code, output = run_cli(
            ['-', '--symbol', 'dispatch', '--format', 'json'],
            f'{self.fixture}\n',
        )
        symbols = {target['symbol'] for target in json.loads(output)['targets']}
        self.assertEqual(code, 0)
        self.assertTrue(symbols)
        self.assertTrue(all('dispatch' in symbol for symbol in symbols))


class FixtureScanTests(unittest.TestCase):
    def test_disk_fixture_matches_the_fixture_module(self) -> None:
        on_disk = fixtures.FIXTURE_MODULE_PATH.read_text(encoding='utf-8')
        self.assertEqual(on_disk, fixtures.SMELLY_MODULE)

    def test_fixture_reports_every_new_rule(self) -> None:
        reported = set(signals(analyze(fixtures.SMELLY_MODULE)))
        expected = {
            SignalName.HS015,
            SignalName.HS016,
            SignalName.HS018,
            SignalName.HS019,
            SignalName.HS021,
        }
        self.assertLessEqual(expected, reported)


class SelfScanTests(unittest.TestCase):
    def package_findings(self) -> dict[str, list[Finding]]:
        return {
            path.name: analyze(path.read_text(encoding='utf-8'))
            for path in sorted(PACKAGE_ROOT.rglob('*.py'))
        }

    def test_no_banned_constructs_in_own_source(self) -> None:
        for name, findings in self.package_findings().items():
            with self.subTest(module=name):
                banned = BANNED_SIGNALS.intersection(signals(findings))
                self.assertEqual(banned, set())

    def test_no_module_exceeds_the_file_threshold(self) -> None:
        for name, findings in self.package_findings().items():
            with self.subTest(module=name):
                self.assertNotIn(SignalName.HS017, signals(findings))

    def test_only_notices_and_baselined_signals_remain(self) -> None:
        allowed = NOTICE_SIGNALS | _baselined_signals()
        remaining = {
            signal
            for findings in self.package_findings().values()
            for signal in signals(findings)
        }
        self.assertLessEqual(remaining, allowed)

    def test_json_report_is_serializable(self) -> None:
        code, output = run_cli([str(PACKAGE_ROOT), '--format', 'json'])
        payload = json.loads(output)
        self.assertEqual(code, 0)
        self.assertGreaterEqual(payload['summary']['files'], 10)
        self.assertEqual(payload['errors'], [])


if __name__ == '__main__':
    unittest.main()
