"""Configuration loading.

Values come from three places, later ones winning: dataclass defaults, a TOML
file, then explicit command line flags. Flags default to ``argparse.SUPPRESS``
so an unset flag is absent from the namespace entirely -- that is what makes
"the file said 80, the flag says 90" resolvable at all.
"""

import argparse
import dataclasses
import tomllib
from collections.abc import Mapping, Sequence
from importlib.metadata import version as package_version
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING

from humansays.const import CLI_DESTINATIONS, DEFAULT_CONFIG_NAMES, PYPROJECT_SECTION
from humansays.enums import FailOn, OutputFormat

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

from .models import (
    ClassThresholds,
    FunctionThresholds,
    ModuleThresholds,
    Report,
    ScannerSettings,
    Selection,
    Thresholds,
)

THRESHOLDS_SPEC = MappingProxyType({
    'functions': FunctionThresholds,
    'classes': ClassThresholds,
    'modules': ModuleThresholds,
})
SETTINGS_SPEC = MappingProxyType({
    'thresholds': (Thresholds, THRESHOLDS_SPEC),
    'selection': Selection,
    'report': Report,
})


class ConfigError(Exception):
    def __init__(self, path: str) -> None:
        super().__init__(f'config file not found: {path}')
        self.path = path


def _build(
    cls: type['DataclassInstance'],
    mapping: Mapping[str, object],
    nested_spec: Mapping[str, object] | None = None,
) -> 'DataclassInstance':
    nested_spec = nested_spec or {}
    known = {f.name for f in dataclasses.fields(cls)}
    unknown = set(mapping) - known
    if unknown:
        raise ValueError(f'unknown keys for {cls.__name__}: {sorted(unknown)}')

    kwargs = {}
    for key, value in mapping.items():
        spec = nested_spec.get(key)
        if spec is None:
            kwargs[key] = value
            continue

        sub_cls, sub_spec = spec if isinstance(spec, tuple) else (spec, None)
        if not isinstance(sub_cls, type):
            raise TypeError(f'nested spec for {key!r} is not a dataclass type')

        if not isinstance(value, Mapping):
            raise TypeError(f'nested value for {key!r} is not a mapping')

        if sub_spec is not None and not isinstance(sub_spec, Mapping):
            raise TypeError(f'nested spec-of-spec for {key!r} is not a mapping')

        # THRESHOLDS_SPEC/SETTINGS_SPEC guarantee dataclass-shaped values here;
        # ty can't see through the isinstance narrowing above.
        kwargs[key] = _build(sub_cls, value, sub_spec)  # ty: ignore[invalid-argument-type]

    return cls(**kwargs)


def build_settings(mapping: Mapping[str, object]) -> ScannerSettings:
    built = _build(ScannerSettings, mapping, SETTINGS_SPEC)
    if not isinstance(built, ScannerSettings):
        raise TypeError(f'expected ScannerSettings, got {type(built).__name__}')

    return built


def toml_values(path: Path) -> dict:
    toml_content = path.read_text()
    data = tomllib.loads(toml_content)
    if path.name != 'pyproject.toml':
        return data

    for key in PYPROJECT_SECTION:
        data = data.get(key, {})

    return data


def _discover_explicit_config(explicit: str) -> Path:
    candidate = Path(explicit)
    if not candidate.is_file():
        raise ConfigError(explicit)

    return candidate


def discover_config(explicit: str | None) -> Path | None:
    if explicit:
        return _discover_explicit_config(explicit)

    for name in DEFAULT_CONFIG_NAMES:
        candidate = Path(name)
        if candidate.is_file():
            return candidate

    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='humansays',
        description=(
            'Find structural Python review leads using the standard-library AST. '
            "Paths may be files or directories; '-' or no path reads a "
            'NUL- or newline-separated file list from standard input.'
        ),
        argument_default=argparse.SUPPRESS,
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {package_version("humansays")}',
    )

    parser.add_argument('paths', nargs='*')
    parser.add_argument('--config')
    parser.add_argument('--format', dest='output_format', choices=tuple(OutputFormat))
    parser.add_argument('--symbol')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--exclude', action='append')
    parser.add_argument('--fail-on', choices=tuple(FailOn))
    parser.add_argument('--min-score', type=float)
    parser.add_argument('--max-arguments', type=int)
    parser.add_argument('--max-nesting', type=int)
    parser.add_argument('--class-nesting-bonus', type=int)
    parser.add_argument('--max-branches', type=int)
    parser.add_argument('--max-function-lines', type=int)
    parser.add_argument('--max-code-lines', type=int)
    parser.add_argument('--max-class-attributes', type=int)
    parser.add_argument('--max-base-classes', type=int)
    parser.add_argument('--max-file-lines', type=int)
    return parser


def place(data: dict, path: Sequence[str], value: object) -> None:
    target = data
    for key in path[:-1]:
        target = target[key]

    target[path[-1]] = value


def apply_overrides(settings: ScannerSettings, overrides: dict) -> ScannerSettings:
    data = dataclasses.asdict(settings)
    cli_destinations = CLI_DESTINATIONS
    for dest, value in overrides.items():
        if destination := cli_destinations.get(dest):
            place(data, destination, value)

    return build_settings(data)


def load_settings(argv: Sequence[str] | None = None) -> ScannerSettings:
    namespace = build_parser().parse_args(argv)
    overrides = vars(namespace)
    resolved_overrides = overrides.pop('config', None)
    config = discover_config(resolved_overrides)
    values = toml_values(config) if config else {}
    return apply_overrides(build_settings(values), overrides)
