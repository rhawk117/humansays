"""Orchestration: resolve inputs, analyze each file, render, choose an exit code.

Version control is deliberately not an input source. The caller decides which
files matter and pipes them in, so any of these work identically::

    humansays src/
    git ls-files -z '*.py' | humansays -
    git diff --name-only --diff-filter=ACM origin/main | humansays -
    rg -l 'subprocess' --type py | humansays -
"""

import logging
from collections.abc import Iterable
from pathlib import Path
from typing import TextIO

from humansays.analysis import RulesetEvaluator, parse_module
from humansays.config.models import ScannerSettings, Selection
from humansays.const import FINDINGS_EXIT, STDIN_SPEC, UNANALYZED_EXIT
from humansays.enums import FailOn, Severity
from humansays.findings.models import Score
from humansays.reporting.models import FileReport, ScanResult

logger = logging.getLogger(__name__)


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
    evaluator = RulesetEvaluator(parsed, settings.thresholds)
    findings = evaluator.run()
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
        classes=len(evaluator.index.classes),
        functions=len(evaluator.index.functions),
        symbols=set(evaluator.index.symbols),
        findings=findings,
    )


def parse_failure(error: SyntaxError) -> str:
    reason = error.msg or 'invalid syntax'
    if error.lineno is None:
        return f'cannot parse: {reason}'

    return f'cannot parse: {reason} (line {error.lineno})'


def is_version_candidate(error: SyntaxError) -> bool:
    """A line number means it tokenized as source, so newer syntax is plausible."""
    return error.lineno is not None


def analyze_paths(paths: Iterable[Path], settings: ScannerSettings) -> ScanResult:
    reports: list[FileReport] = []
    errors: list[str] = []
    unparsed = 0
    potential_exceptions = (OSError, UnicodeError, SyntaxError, ValueError)
    for path in paths:
        try:
            logger.debug('analyzing %s', path)
            reports.append(analyze_file(path, settings))
        except potential_exceptions as error:
            if isinstance(error, SyntaxError):
                unparsed += is_version_candidate(error)
                message = f'{path}: {parse_failure(error)}'
            else:
                message = f'{path}: {error}'

            logger.warning('not analyzed %s', message)
            errors.append(message)

    logger.info('analyzed %d of %d files', len(reports), len(reports) + len(errors))
    named = [spec for spec in settings.selection.paths if spec != STDIN_SPEC]
    return ScanResult(
        label=', '.join(named) or '<stdin>',
        reports=reports,
        errors=errors,
        unparsed=unparsed,
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
    """Findings outrank unanalyzed input, so a caller already keying on 1 is safe.

    ``UNANALYZED_EXIT`` therefore surfaces only on a run that would otherwise be
    clean -- which is exactly the run that used to report a false success.
    """
    if score.value < settings.report.min_score:
        return FINDINGS_EXIT

    if settings.report.fail_on is not FailOn.NEVER:
        severity = severity_exit(result, settings.report.fail_on)
        if severity:
            return severity

    if result.errors:
        return UNANALYZED_EXIT

    return 0


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
