"""Golden JSON parity harness.

Transforms the raw pysignals 0.3.0 oracle (PY ids, three now-deleted rules) into
the shape humansays should produce (HS ids, deleted rules dropped, score
recomputed from the survivors) and asserts it against what humansays actually
finds when it analyzes the same vendored corpus. This is the migration's
acceptance criterion: identical findings, identical scores, modulo the rename
and the three deletions.
"""

import ast
import json
import tomllib
from pathlib import Path

from humansays.analysis.models import ParsedModule
from humansays.analysis.rules import RulesetEvaluator
from humansays.config.models import Thresholds
from humansays.enums import Grade
from humansays.reporting.models import FileReport, ScanResult
from humansays.scoring import score_for

HERE = Path(__file__).resolve().parent
POC_PARITY = HERE / 'poc-parity'
REPO_ROOT = HERE.parent.parent

MANIFEST = tomllib.loads((POC_PARITY / 'manifest.toml').read_text(encoding='utf-8'))
MAPPING = tomllib.loads((POC_PARITY / 'mapping.toml').read_text(encoding='utf-8'))
DELETED_IDS = frozenset(MAPPING['deleted'])
RENAME = MAPPING['rename']

GRADE_BANDS = ((90.0, Grade.A), (75.0, Grade.B), (60.0, Grade.C), (40.0, Grade.D))


def _grade_for(value: float) -> str:
    for floor, grade in GRADE_BANDS:
        if value >= floor:
            return str(grade)
    return str(Grade.F)


def _transform_oracle(raw: dict) -> dict:
    survivors = [
        finding for finding in raw['findings'] if finding['rule_id'] not in DELETED_IDS
    ]
    for finding in survivors:
        finding['rule_id'] = RENAME[finding['rule_id']]
    penalty = round(
        sum(finding['weight'] * finding['confidence'] for finding in survivors), 2
    )
    lines = raw['score']['lines']
    density = round(penalty * 100 / lines, 3)
    value = round(100 / (1 + density / 7.5), 1)
    return {
        'findings': sorted(
            (
                (f['path'], f['line'], f['rule_id'], f['symbol'], f['end_line'])
                for f in survivors
            ),
        ),
        'score': {
            'lines': lines,
            'penalty': penalty,
            'density': density,
            'value': value,
            'grade': _grade_for(value),
        },
    }


def _humansays_findings(group: dict) -> dict:
    root = REPO_ROOT / group['root']
    reports = []
    findings_out = []
    for rel in group['files']:
        path = root / rel
        source = path.read_text(encoding='utf-8')
        module = ParsedModule(path, source, ast.parse(source, filename=str(path)))
        findings = RulesetEvaluator(module, Thresholds()).run()
        reports.append(FileReport(path, len(source.splitlines()), 0, 0, set(), findings))
        findings_out.extend(
            (
                rel,
                finding.location.line,
                finding.rule.rule_id,
                finding.location.symbol,
                finding.location.end_line,
            )
            for finding in findings
        )
    score = score_for(ScanResult('<group>', reports, []))
    return {
        'findings': sorted(findings_out),
        'score': {
            'lines': score.lines,
            'penalty': score.penalty,
            'density': score.density,
            'value': score.value,
            'grade': str(score.grade),
        },
    }


def _group_names() -> list[str]:
    return list(MANIFEST['groups'])


def test_every_group_has_a_frozen_oracle() -> None:
    for name in _group_names():
        assert (POC_PARITY / f'{name}.raw.json').is_file()


def test_humansays_matches_transformed_oracle_for_every_group() -> None:
    for name in _group_names():
        raw = json.loads((POC_PARITY / f'{name}.raw.json').read_text(encoding='utf-8'))
        expected = _transform_oracle(raw)
        actual = _humansays_findings(MANIFEST['groups'][name])

        assert actual['findings'] == expected['findings'], (
            f'group {name!r} findings diverge'
        )
        assert actual['score'] == expected['score'], f'group {name!r} score diverges'


def test_poc_group_grouped_json_smoke() -> None:
    """poc is all-notices; after deletion it should render an empty, perfect scan."""
    from humansays import application
    from humansays.config.models import Report, ScannerSettings, Selection
    from humansays.enums import OutputFormat
    from humansays.reporting.payload import json_payload

    group = MANIFEST['groups']['poc']
    root = REPO_ROOT / group['root']
    paths = [str(root / rel) for rel in group['files']]

    settings = ScannerSettings(
        selection=Selection(paths=tuple(paths)),
        report=Report(format=OutputFormat.JSON, limit=0),
    )
    files = application.collect_files(paths, settings.selection.excludes)
    result = application.analyze_paths(files, settings)
    score = score_for(result)
    payload = json_payload(result, score, settings.report)

    assert payload['schema_version'] == 1
    assert payload['targets'] == []
    assert payload['score']['value'] == 100.0
