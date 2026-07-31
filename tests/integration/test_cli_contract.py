"""The CLI's observable contract: scoring, configuration, input resolution, and
the scan humansays runs against its own source.

Every test here drives `main()` end to end rather than calling the evaluator, so
what it asserts is what a caller at a shell would see.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from humansays.analysis.extraction import extract
from humansays.analysis.models import ParsedModule
from humansays.cli import main
from humansays.config.models import Thresholds
from humansays.enums import Disposition, Grade, SignalName
from humansays.rules import evaluate, registry
from humansays.rules.loading import rule_definitions
from tests.fixtures.sweeps import python_sources

if TYPE_CHECKING:
    from humansays.findings.models import Finding

BANNED_SIGNALS = frozenset({SignalName.HS015, SignalName.HS016})
NOTICE_SIGNALS = frozenset()


def analyze(source: str, thresholds: Thresholds | None = None) -> list[Finding]:
    module = ParsedModule(Path('<snippet>'), source, ast.parse(source))
    return evaluate(extract(module), thresholds or Thresholds())


def signals(findings: list[Finding]) -> list[SignalName]:
    return [finding.rule.signal for finding in findings]


def run_cli(argv: list[str], piped: str = '') -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(io.StringIO()):
        code = main(argv, io.StringIO(piped))
    return code, buffer.getvalue()


def package_findings(src_root: Path) -> dict[str, list[Finding]]:
    return {
        path.name: analyze(path.read_text(encoding='utf-8'))
        for path in python_sources(src_root)
    }


def baselined_signals(baseline_path: Path) -> frozenset[SignalName]:
    entries = json.loads(baseline_path.read_text(encoding='utf-8'))['entries']
    return frozenset(SignalName[entry['rule_id']] for entry in entries)


def reported_rule_ids(output: str) -> set[str]:
    payload = json.loads(output)
    return {
        signal['rule_id'] for target in payload['targets'] for signal in target['signals']
    }


class TestScoring:
    def test_clean_source_scores_an_a(self, src_root: Path) -> None:
        _, output = run_cli([str(src_root), '--format', 'json'])
        score = json.loads(output)['score']
        assert score['grade'] == Grade.A

    def test_smelly_source_scores_badly(self, smelly_module_path: Path) -> None:
        _, output = run_cli(['--format', 'json'], str(smelly_module_path))
        score = json.loads(output)['score']
        assert score['value'] < 60.0
        assert score['penalty'] > 0.0

    def test_min_score_gates_the_exit_code(self, smelly_module_path: Path) -> None:
        code, _ = run_cli(['--min-score', '90'], str(smelly_module_path))
        assert code == 1


class TestConfiguration:
    def test_toml_thresholds_are_applied(
        self,
        config_toml_path: Path,
        smelly_module_path: Path,
    ) -> None:
        code, output = run_cli(
            [
                '--config',
                str(config_toml_path),
                '--format',
                'json',
                '--min-score',
                '0',
            ],
            str(smelly_module_path),
        )
        assert code == 0
        assert 'HS017' in reported_rule_ids(output)

    def test_command_line_overrides_the_file(
        self,
        config_toml_path: Path,
        smelly_module_path: Path,
    ) -> None:
        code, output = run_cli(
            [
                '--config',
                str(config_toml_path),
                '--format',
                'json',
                '--max-file-lines',
                '5000',
                '--min-score',
                '0',
            ],
            str(smelly_module_path),
        )
        assert code == 0
        assert 'HS017' not in reported_rule_ids(output)

    def test_file_min_score_can_fail_the_run(
        self,
        config_toml_path: Path,
        smelly_module_path: Path,
    ) -> None:
        code, _ = run_cli(
            ['--config', str(config_toml_path)],
            str(smelly_module_path),
        )
        assert code == 1


class TestInputResolution:
    def test_paths_can_be_piped_on_stdin(self, smelly_module_path: Path) -> None:
        code, output = run_cli(['--format', 'json'], f'{smelly_module_path}\n')
        payload = json.loads(output)
        assert code == 0
        assert payload['summary']['files'] == 1
        assert payload['root'] == '<stdin>'

    def test_nul_separated_paths_are_accepted(self, smelly_module_path: Path) -> None:
        code, output = run_cli(['-', '--format', 'json'], f'{smelly_module_path}\0')
        assert code == 0
        assert json.loads(output)['summary']['files'] == 1

    def test_fail_on_warning_sets_exit_code(self, smelly_module_path: Path) -> None:
        code, _ = run_cli(['-', '--fail-on', 'warning'], f'{smelly_module_path}\n')
        assert code == 1

    def test_fail_on_never_is_the_default(self, smelly_module_path: Path) -> None:
        code, _ = run_cli(['-'], f'{smelly_module_path}\n')
        assert code == 0

    def test_missing_paths_exit_three(self) -> None:
        code, _ = run_cli(['-'], '/nonexistent/path.py\n')
        assert code == 3

    def test_unknown_symbol_exits_two(self, smelly_module_path: Path) -> None:
        code, _ = run_cli(['-', '--symbol', 'nope'], f'{smelly_module_path}\n')
        assert code == 2

    def test_symbol_filter_narrows_targets(self, smelly_module_path: Path) -> None:
        code, output = run_cli(
            ['-', '--symbol', 'dispatch', '--format', 'json'],
            f'{smelly_module_path}\n',
        )
        symbols = {target['symbol'] for target in json.loads(output)['targets']}
        assert code == 0
        assert symbols
        assert all('dispatch' in symbol for symbol in symbols)


class TestEvidenceDisposition:
    """Invariant 4 of the phase C2 plan, driven through `main()`.

    No shipped rule is `evidence`, so HS003 is re-dispositioned onto a
    test-only definition map. That is what invariant 4 asks for, and it is
    also the only way to reach the flag at all: a test drawing on the shipped
    definitions could not produce an evidence finding to hide.

    `tests/unit/test_evidence_display.py` covers the same filter at the
    `review_targets` seam. This one exists because that seam is reached
    through `--show-evidence` -> `CLI_DESTINATIONS` -> `Report.show_evidence`,
    and none of that chain is exercised by calling `review_targets` directly.
    """

    @staticmethod
    def redispositioned(
        monkeypatch: pytest.MonkeyPatch,
        disposition: Disposition,
    ) -> None:
        definitions = dict(rule_definitions())
        definition = definitions[SignalName.HS003]
        definitions[SignalName.HS003] = replace(
            definition,
            spec=replace(definition.spec, disposition=disposition),
        )
        monkeypatch.setattr(registry, 'rule_definitions', lambda: definitions)

    @pytest.fixture
    def hidden_hs003(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.redispositioned(monkeypatch, Disposition.EVIDENCE)

    @pytest.fixture
    def off_hs003(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.redispositioned(monkeypatch, Disposition.OFF)

    def test_hs003_is_reported_before_it_is_re_dispositioned(
        self,
        smelly_module_path: Path,
    ) -> None:
        """Without this, the two assertions below pass on an empty report."""
        _, output = run_cli(['--format', 'json'], str(smelly_module_path))
        assert 'HS003' in reported_rule_ids(output)

    @pytest.mark.usefixtures('hidden_hs003')
    def test_evidence_is_withheld_by_default(self, smelly_module_path: Path) -> None:
        _, output = run_cli(['--format', 'json'], str(smelly_module_path))
        assert 'HS003' not in reported_rule_ids(output)

    @pytest.mark.usefixtures('hidden_hs003')
    def test_show_evidence_reveals_it(self, smelly_module_path: Path) -> None:
        _, output = run_cli(
            ['--format', 'json', '--show-evidence'],
            str(smelly_module_path),
        )
        assert 'HS003' in reported_rule_ids(output)

    @pytest.mark.usefixtures('off_hs003')
    def test_off_is_not_emitted_even_with_show_evidence(
        self,
        smelly_module_path: Path,
    ) -> None:
        """`off` short-circuits at emission, which is what separates it from
        `evidence`: no flag can reveal a finding that was never built."""
        _, output = run_cli(
            ['--format', 'json', '--show-evidence'],
            str(smelly_module_path),
        )
        assert 'HS003' not in reported_rule_ids(output)


class TestSelfScan:
    def test_no_banned_constructs_in_own_source(self, src_root: Path) -> None:
        offenders = {
            name: sorted(banned)
            for name, findings in package_findings(src_root).items()
            if (banned := BANNED_SIGNALS.intersection(signals(findings)))
        }
        assert offenders == {}

    def test_no_module_exceeds_the_file_threshold(self, src_root: Path) -> None:
        offenders = [
            name
            for name, findings in package_findings(src_root).items()
            if SignalName.HS017 in signals(findings)
        ]
        assert offenders == []

    def test_only_notices_and_baselined_signals_remain(
        self,
        src_root: Path,
        baseline_path: Path,
    ) -> None:
        allowed = NOTICE_SIGNALS | baselined_signals(baseline_path)
        remaining = {
            signal
            for findings in package_findings(src_root).values()
            for signal in signals(findings)
        }
        assert remaining <= allowed

    def test_json_report_is_serializable(self, src_root: Path) -> None:
        code, output = run_cli([str(src_root), '--format', 'json'])
        payload = json.loads(output)
        assert code == 0
        assert payload['summary']['files'] >= 10
        assert payload['errors'] == []
