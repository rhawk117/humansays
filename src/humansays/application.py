"""Orchestration: resolve inputs, analyze each file, render, choose an exit code.

Version control is deliberately not an input source. The caller decides which
files matter and pipes them in, so any of these work identically::

    humansays src/
    git ls-files -z '*.py' | humansays -
    git diff --name-only --diff-filter=ACM origin/main | humansays -
    rg -l 'subprocess' --type py | humansays -
"""

from collections.abc import Iterable
from pathlib import Path
from typing import TextIO

from .analysis import Analyzer, parse_module
from .config.models import ScannerSettings, Selection
from .const import FINDINGS_EXIT, STDIN_SPEC
from .enums import FailOn, Severity
from .findings.models import Score
from .reporting.models import FileReport, ScanResult


def read_stream_paths(stream: TextIO) -> list[str]:
    data = stream.read()
    separator = '\0' if '\0' in data else '\n'
    return [item.strip() for item in data.split(separator) if item.strip()]


def resolve_specs(selection: Selection, stream: TextIO) -> list[str]:
    if not selection.paths:
        return read_stream_paths(stream)

    specs: list[str] = []
    for spec in selection.paths:
        if spec == STDIN_SPEC:
            specs.extend(read_stream_paths(stream))
        else:
            specs.append(spec)

    return specs


def is_included_python_file(
    candidate: Path,
    root: Path,
    excludes: frozenset[str],
) -> bool:
    if candidate.suffix != '.py' or not candidate.is_file():
        return False

    try:
        relative = candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return False

    directories = relative.parts[:-1]
    hidden = any(part.startswith('.') for part in directories)
    return not hidden and not excludes.intersection(relative.parts)


def expand_spec(spec: str, excludes: frozenset[str]) -> list[Path]:
    path = Path(spec)
    if path.is_file():
        return [path] if path.suffix == '.py' else []

    if not path.is_dir():
        return []

    return [
        candidate
        for candidate in sorted(path.rglob('*.py'))
        if is_included_python_file(candidate, path, excludes)
    ]


def collect_files(specs: Iterable[str], excludes: frozenset[str]) -> list[Path]:
    seen: dict[Path, None] = {}
    for spec in specs:
        for path in expand_spec(spec, excludes):
            seen.setdefault(path, None)

    return list(seen)


def matches_symbol(symbol: str, wanted: str) -> bool:
    return (
        symbol == wanted
        or symbol.endswith(f'.{wanted}')
        or symbol.startswith(f'{wanted}.')
    )


def analyze_file(path: Path, settings: ScannerSettings) -> FileReport:
    parsed = parse_module(path)
    analyzer = Analyzer(parsed, settings.thresholds)
    findings = analyzer.run()
    wanted = settings.selection.symbol
    if wanted:
        findings = [
            finding
            for finding in findings
            if matches_symbol(finding.location.symbol, wanted)
        ]

    return FileReport(
        path=path,
        lines=len(parsed.lines),
        classes=len(analyzer.index.classes),
        functions=len(analyzer.index.functions),
        symbols=set(analyzer.index.symbols),
        findings=findings,
    )


def analyze_paths(paths: Iterable[Path], settings: ScannerSettings) -> ScanResult:
    reports: list[FileReport] = []
    errors: list[str] = []
    potential_exceptions = (OSError, UnicodeError, SyntaxError, ValueError)
    for path in paths:
        try:
            reports.append(analyze_file(path, settings))
        except potential_exceptions as error:
            errors.append(f'{path}: {error}')

    named = [spec for spec in settings.selection.paths if spec != STDIN_SPEC]
    return ScanResult(
        label=', '.join(named) or '<stdin>',
        reports=reports,
        errors=errors,
    )


def symbol_is_present(result: ScanResult, wanted: str) -> bool:
    return any(
        matches_symbol(symbol, wanted)
        for report in result.reports
        for symbol in report.symbols
    )


def severity_exit(result: ScanResult, fail_on: FailOn) -> int:
    findings = result.findings
    if fail_on is FailOn.ANY and findings:
        return FINDINGS_EXIT

    warnings = [
        finding for finding in findings if finding.rule.severity is Severity.WARNING
    ]
    if fail_on is FailOn.WARNING and warnings:
        return FINDINGS_EXIT

    return 0


def exit_code(result: ScanResult, score: Score, settings: ScannerSettings) -> int:
    if score.value < settings.report.min_score:
        return FINDINGS_EXIT

    if settings.report.fail_on is FailOn.NEVER:
        return 0

    return severity_exit(result, settings.report.fail_on)


__all__ = (
    'analyze_file',
    'analyze_paths',
    'collect_files',
    'exit_code',
    'expand_spec',
    'is_included_python_file',
    'matches_symbol',
    'read_stream_paths',
    'resolve_specs',
    'severity_exit',
    'symbol_is_present',
)
