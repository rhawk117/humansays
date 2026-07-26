"""Scan result models.

``FileReport`` is what one file contributed; ``ScanResult`` is everything the
run produced, across every file.
"""

from dataclasses import dataclass
from pathlib import Path

from humansays.findings.models import Finding


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
