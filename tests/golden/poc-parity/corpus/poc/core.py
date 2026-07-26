"""Orchestration: resolve inputs, analyze each file, render, choose an exit code.

Version control is deliberately not an input source. The caller decides which
files matter and pipes them in, so any of these work identically::

    pysignals src/
    git ls-files -z '*.py' | pysignals -
    git diff --name-only --diff-filter=ACM origin/main | pysignals -
    rg -l 'subprocess' --type py | pysignals -
"""

import ast
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import TextIO

from .const import FINDINGS_EXIT, MISSING_SYMBOL_EXIT, NO_FILES_EXIT, STDIN_SPEC
from .enums import FailOn, Severity
from .models import FileReport, ParsedModule, ScanResult, Score, Selection
from .options import ScannerSettings, load_settings
from .report import emit
from .rules import Analyzer
from .scoring import score_for


def read_stream_paths(stream: TextIO) -> list[str]:
    data = stream.read()
    separator = "\0" if "\0" in data else "\n"
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
    if candidate.suffix != ".py" or not candidate.is_file():
        return False
    try:
        relative = candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    directories = relative.parts[:-1]
    hidden = any(part.startswith(".") for part in directories)
    return not hidden and not excludes.intersection(relative.parts)


def expand_spec(spec: str, excludes: frozenset[str]) -> list[Path]:
    path = Path(spec)
    if path.is_file():
        return [path] if path.suffix == ".py" else []
    if not path.is_dir():
        return []
    return [
        candidate
        for candidate in sorted(path.rglob("*.py"))
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
        or symbol.endswith(f".{wanted}")
        or symbol.startswith(f"{wanted}.")
    )


def analyze_file(path: Path, settings: ScannerSettings) -> FileReport:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path), type_comments=True)
    analyzer = Analyzer(ParsedModule(path, source, tree), settings.thresholds)
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
        lines=len(source.splitlines()),
        classes=len(analyzer.index.classes),
        functions=len(analyzer.index.functions),
        symbols=set(analyzer.index.symbols),
        findings=findings,
    )


def analyze_paths(paths: Iterable[Path], settings: ScannerSettings) -> ScanResult:
    reports: list[FileReport] = []
    errors: list[str] = []
    for path in paths:
        try:
            reports.append(analyze_file(path, settings))
        except (OSError, UnicodeError, SyntaxError, ValueError) as error:
            errors.append(f"{path}: {error}")
    named = [spec for spec in settings.selection.paths if spec != STDIN_SPEC]
    return ScanResult(
        label=", ".join(named) or "<stdin>",
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


def main(argv: Sequence[str] | None = None, stream: TextIO | None = None) -> int:
    settings = load_settings(argv)
    specs = resolve_specs(settings.selection, stream or sys.stdin)
    paths = collect_files(specs, settings.selection.excludes)
    if not paths:
        source = ", ".join(specs) or "<stdin>"
        print(f"error: no Python files found in {source}", file=sys.stderr)
        return NO_FILES_EXIT

    result = analyze_paths(paths, settings)
    wanted = settings.selection.symbol
    if wanted and not symbol_is_present(result, wanted):
        print(f"error: symbol {wanted!r} not found", file=sys.stderr)
        return MISSING_SYMBOL_EXIT

    score = score_for(result)
    emit(result, score, settings.report)
    return exit_code(result, score, settings)
