from __future__ import annotations

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
    print(
        f'verified {project_meta.distribution_name} {installed_version} '
        f'through the {project_meta.cli_name!r} entry point'
    )
    return 0


def main() -> None:
    try:
        smoke_test()
    except Exception as exc:
        fail(f'unhandled runtime exception: `{exc!r}`')


if __name__ == '__main__':
    main()
