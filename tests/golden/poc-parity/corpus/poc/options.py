"""Configuration.

Values come from four places, later ones winning: model defaults, environment
variables (``PYSIGNALS_REPORT__MIN_SCORE=70``), a TOML file, then explicit
command line flags. Flags default to ``argparse.SUPPRESS`` so an unset flag is
absent from the namespace entirely — that is what makes "the file said 80, the
flag says 90" resolvable at all.
"""

import argparse
from collections.abc import Sequence
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict, TomlConfigSettingsSource

from .const import CLI_DESTINATIONS, DEFAULT_CONFIG_NAMES, PYPROJECT_SECTION
from .enums import FailOn, OutputFormat
from .models import Report, Selection, Thresholds


class ScannerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PYSIGNALS_",
        env_nested_delimiter="__",
        extra="forbid",
        frozen=True,
    )

    thresholds: Thresholds = Thresholds()
    selection: Selection = Selection()
    report: Report = Report()


def toml_values(path: Path) -> dict:
    values = TomlConfigSettingsSource(ScannerSettings, toml_file=path)()
    if path.name != "pyproject.toml":
        return values
    for key in PYPROJECT_SECTION:
        values = values.get(key, {})
    return values


def discover_config(explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit)
    for name in DEFAULT_CONFIG_NAMES:
        candidate = Path(name)
        if candidate.is_file():
            return candidate
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pysignals",
        description=(
            "Find structural Python review leads using the standard-library AST. "
            "Paths may be files or directories; '-' or no path reads a "
            "NUL- or newline-separated file list from standard input."
        ),
        argument_default=argparse.SUPPRESS,
    )
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--config")
    parser.add_argument("--format", dest="output_format", choices=tuple(OutputFormat))
    parser.add_argument("--symbol")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--exclude", action="append")
    parser.add_argument("--fail-on", choices=tuple(FailOn))
    parser.add_argument("--min-score", type=float)
    parser.add_argument("--max-arguments", type=int)
    parser.add_argument("--max-nesting", type=int)
    parser.add_argument("--class-nesting-bonus", type=int)
    parser.add_argument("--max-branches", type=int)
    parser.add_argument("--max-function-lines", type=int)
    parser.add_argument("--max-code-lines", type=int)
    parser.add_argument("--max-class-attributes", type=int)
    parser.add_argument("--max-base-classes", type=int)
    parser.add_argument("--max-file-lines", type=int)
    return parser


def place(data: dict, path: Sequence[str], value: object) -> None:
    target = data
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def apply_overrides(settings: ScannerSettings, overrides: dict) -> ScannerSettings:
    data = settings.model_dump()
    for dest, value in overrides.items():
        destination = CLI_DESTINATIONS.get(dest)
        if destination is not None:
            place(data, destination, value)
    return ScannerSettings(**data)


def load_settings(argv: Sequence[str] | None = None) -> ScannerSettings:
    namespace = build_parser().parse_args(argv)
    overrides = vars(namespace)
    config = discover_config(overrides.pop("config", None))
    values = toml_values(config) if config else {}
    return apply_overrides(ScannerSettings(**values), overrides)
