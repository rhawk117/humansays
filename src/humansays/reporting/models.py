"""Scan result models.

``FileReport`` is what one file contributed; ``ScanResult`` is everything the
run produced, across every file. ``ReportRequest`` is what a renderer needs to
write that run out.
"""

from dataclasses import dataclass
from pathlib import Path

from humansays.config.models import Report
from humansays.findings.models import Finding, Score


@dataclass(frozen=True, slots=True)
class FileReport:
    path: Path
    lines: int
    classes: int
    functions: int
    symbols: set[str]
    findings: list[Finding]


@dataclass(frozen=True, slots=True)
class ScanResult:
    label: str
    reports: list[FileReport]
    errors: list[str]

    @property
    def findings(self) -> list[Finding]:
        return [finding for report in self.reports for finding in report.findings]

    @property
    def lines(self) -> int:
        return sum(report.lines for report in self.reports)


@dataclass(frozen=True, slots=True)
class ReportRequest:
    """One run, ready to be written out.

    The four values always travel together, so renderers take this rather
    than passing them down one at a time.
    """

    result: ScanResult
    score: Score
    settings: Report
    exit_code: int

    @property
    def failed(self) -> bool:
        """Whether the caller is treating this run as a failure."""
        return self.exit_code != 0
