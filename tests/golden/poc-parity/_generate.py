"""One-time generator for the poc-parity golden oracle. NOT a test.

Run under an environment with the untainted pysignals 0.3.0 POC installed:

    uv run --python 3.12 --with .poc-reference/pysignals-0.3.0 --no-project -- \\
        python tests/golden/poc-parity/_generate.py \\
        --root django=/path/to/extracted/Django-5.1.4

The django group's root must be supplied on the command line: the manifest
only pins the sdist URL/sha256, not a local extraction path, so the sdist can
be re-fetched and re-verified independently of wherever it happens to be
unpacked on the generating machine.

Writes, for every group in manifest.toml: <group>.raw.json (the authoritative
per-finding oracle used by tests/golden/test_parity.py) plus <group>.pysignals.json
and <group>.pysignals.txt (reference-only CLI output, NOT asserted against for
groups whose CLI JSON aggregates multiple findings per symbol).
"""

import argparse
import ast
import contextlib
import io
import json
import sys
import tomllib
from pathlib import Path

from pysignals.core import main as cli_main
from pysignals.models import FileReport, ParsedModule, ScanResult, Thresholds
from pysignals.rules import Analyzer
from pysignals.scoring import score_for

HERE = Path(__file__).resolve().parent


def raw_findings(path: Path) -> tuple[list, int]:
    src = path.read_text(encoding='utf-8')
    tree = ast.parse(src, filename=str(path), type_comments=True)
    analyzer = Analyzer(ParsedModule(path, src, tree), Thresholds())
    findings = analyzer.run()
    return findings, len(src.splitlines())


def dump_group(files: list[tuple[str, Path]]) -> dict:
    findings_out = []
    reports = []
    for rel, path in files:
        findings, nlines = raw_findings(path)
        reports.append(FileReport(path, nlines, 0, 0, set(), findings))
        findings_out.extend(
            {
                'path': rel,
                'rule_id': finding.rule.rule_id,
                'symbol': finding.location.symbol,
                'line': finding.location.line,
                'end_line': finding.location.end_line,
                'weight': finding.rule.weight,
                'confidence': finding.rule.confidence,
                'message': finding.observation.message,
                'evidence': list(finding.observation.evidence),
            }
            for finding in findings
        )
    score = score_for(ScanResult('<group>', reports, []))
    return {
        'findings': sorted(
            findings_out, key=lambda f: (f['path'], f['line'], f['rule_id'])
        ),
        'score': {
            'lines': score.lines,
            'penalty': score.penalty,
            'density': score.density,
            'value': score.value,
            'grade': str(score.grade),
        },
    }


def run_cli(argv: list[str]) -> str:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(io.StringIO()):
        cli_main(argv, io.StringIO(''))
    return buffer.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--root',
        action='append',
        default=[],
        metavar='GROUP=PATH',
        help="override a group's root path (required if no repo-relative root)",
    )
    args = parser.parse_args()
    overrides = dict(item.split('=', 1) for item in args.root)

    manifest = tomllib.loads((HERE / 'manifest.toml').read_text(encoding='utf-8'))
    repo_root = HERE.parent.parent.parent

    for group_name, group in manifest['groups'].items():
        root = Path(overrides.get(group_name, group.get('root', '')))
        if not root.is_absolute():
            root = (repo_root / root).resolve()
        files = [(rel, root / rel) for rel in group['files']]
        missing = [path for _, path in files if not path.is_file()]
        if missing:
            print(
                f'error: group {group_name!r} missing files: {missing}', file=sys.stderr
            )
            raise SystemExit(1)

        raw = dump_group(files)
        (HERE / f'{group_name}.raw.json').write_text(
            json.dumps(raw, indent=2) + '\n',
            encoding='utf-8',
        )

        absolute = [str(path) for _, path in files]
        json_output = run_cli(['--format', 'json', '--limit', '0', *absolute])
        (HERE / f'{group_name}.pysignals.json').write_text(json_output, encoding='utf-8')

        text_output = run_cli(['--format', 'text', '--limit', '0', *absolute])
        (HERE / f'{group_name}.pysignals.txt').write_text(text_output, encoding='utf-8')

        print(f'{group_name}: {len(raw["findings"])} findings, score={raw["score"]}')


if __name__ == '__main__':
    main()
