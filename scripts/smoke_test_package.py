from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tomllib
from contextlib import suppress
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, NoReturn


@dataclass(slots=True, frozen=True)
class PyprojectMetadata:
    distribution_name: str
    version: str
    scripts: dict[str, Any]

    @property
    def cli_name(self) -> str:
        return next(iter(self.scripts))

    def get_installed_version(self) -> str | None:
        with suppress(PackageNotFoundError):
            return version(self.distribution_name)

        return None


def fail(message: str) -> NoReturn:
    print(f'::error::{message}', file=sys.stderr)
    raise SystemExit(1)


def read_pyproject_project(file: str = 'pyproject.toml') -> dict[str, Any]:
    contents = Path(file).resolve().read_text()
    document = tomllib.loads(contents)

    project = document.get('project')
    if not isinstance(project, dict):
        fail('pyproject.toml does not contain [project] metadata')

    return project


def load_pyproject_meta(project: dict[str, Any]) -> PyprojectMetadata:
    distribution_name = project.get('name')
    expected_version = project.get('version')
    scripts = project.get('scripts')

    if not isinstance(distribution_name, str):
        fail('[project].name must be a string')

    if not isinstance(expected_version, str):
        fail('[project].version must be a string')

    if not isinstance(scripts, dict) or not scripts:
        fail('[project.scripts] must contain at least one CLI')

    return PyprojectMetadata(
        distribution_name=distribution_name,
        version=expected_version,
        scripts=scripts,
    )


def validate_package_cli(project: PyprojectMetadata) -> None:
    arguments = ('--version', '--help')
    for arg in arguments:
        result = subprocess.run(  # noqa: S603
            [project.cli_name, arg],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            fail(
                f'{project.cli_name} {arg} failed with '
                f'status {result.returncode}\n'
                f'stdout:\n{result.stdout}\n'
                f'stderr:\n{result.stderr}'
            )


FIXTURE_DIRECTORY = 'tests/golden/poc-parity/corpus/poc'
REQUIRED_SUMMARY_KEYS = frozenset({
    'files',
    'lines',
    'targets',
    'signals',
    'errors',
    'truncated',
})


def run_cli(cli: str, *arguments: str) -> str:
    result = subprocess.run(  # noqa: S603
        [cli, *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(
            f'{cli} {" ".join(arguments)} failed with status '
            f'{result.returncode}\nstdout:\n{result.stdout}\n'
            f'stderr:\n{result.stderr}'
        )
    return result.stdout


def validate_scan_json(payload: str, label: str) -> None:
    try:
        document = json.loads(payload)
    except json.JSONDecodeError as error:
        fail(f'{label}: output was not valid JSON: {error}')

    if document.get('schema_version') != 1:
        fail(
            f'{label}: expected schema_version 1, got {document.get("schema_version")!r}'
        )

    summary = document.get('summary')
    if not isinstance(summary, dict):
        fail(f'{label}: payload has no summary object')

    if missing := REQUIRED_SUMMARY_KEYS - set(summary):
        fail(f'{label}: summary is missing {sorted(missing)}')

    if summary['files'] < 1:
        fail(f'{label}: scanned zero files')

    if summary['errors']:
        fail(f'{label}: scan reported {summary["errors"]} parse error(s)')


def installed_package_directory() -> str:
    """Locate the installed package so the self-scan reads the artifact.

    Importing `humansays` here is importing our own package, not third-party
    code under analysis, so the no-import-to-analyze rule does not apply.
    """
    specification = importlib.util.find_spec('humansays')
    if specification is None or not specification.submodule_search_locations:
        fail('humansays is importable by name but has no package directory')
    return str(specification.submodule_search_locations[0])


def validate_fixture_scan(project: PyprojectMetadata) -> None:
    fixture = Path(FIXTURE_DIRECTORY)
    if not fixture.is_dir():
        fail(f'fixture directory {FIXTURE_DIRECTORY} not found; run from the repo root')

    payload = run_cli(project.cli_name, '--format', 'json', str(fixture))
    validate_scan_json(payload, f'fixture scan of {FIXTURE_DIRECTORY}')


def validate_self_scan(project: PyprojectMetadata) -> None:
    package_directory = installed_package_directory()
    if str(Path.cwd().resolve()) in package_directory:
        fail(
            f'installed package resolved inside the source tree '
            f'({package_directory}); the artifact is not isolated'
        )

    payload = run_cli(project.cli_name, '--format', 'json', package_directory)
    validate_scan_json(payload, f'self-scan of {package_directory}')


def smoke_test() -> int:
    project_section = read_pyproject_project()
    project_meta = load_pyproject_meta(project_section)

    if not (installed_version := project_meta.get_installed_version()):
        fail(f'{project_meta.distribution_name!r} was not installed from the wheel')

    if installed_version != project_meta.version:
        fail(
            f'installed version {installed_version!r} does not match '
            f'project version {project_meta.version!r}'
        )

    validate_package_cli(project_meta)
    validate_fixture_scan(project_meta)
    validate_self_scan(project_meta)
    print(
        f'verified {project_meta.distribution_name} {installed_version} '
        f'through the {project_meta.cli_name!r} entry point'
    )
    return 0


def main() -> None:
    try:
        smoke_test()
    except Exception as exc:  # noqa: BLE001 - the smoke test reports any failure as one message
        fail(f'unhandled runtime exception: `{exc!r}`')


if __name__ == '__main__':
    main()
