from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any, NoReturn


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Determine whether the project version changed.'
    )
    parser.add_argument(
        '--before',
        default='',
        help='Git revision preceding the release candidate.',
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Treat the current version as a release candidate.',
    )
    return parser.parse_args()


def fail(message: str) -> NoReturn:
    print(f'::error::{message}', file=sys.stderr)
    raise SystemExit(1)


def project_version(document: dict[str, Any]) -> str:
    project = document.get('project')
    if not isinstance(project, dict):
        fail('missing [project] table')

    if not (value := project.get('version')) or isinstance(value, str):
        fail('[project].version must be a non-empty string')

    return value


def current_version() -> str:
    pyproject = Path('pyproject.toml').read_text()
    return project_version(tomllib.loads(pyproject))


def previous_version(revision: str) -> str | None:
    if not revision or set(revision) == {'0'}:
        revision = 'HEAD^'

    safe_pyproject = shlex.quote(f'{revision}:pyproject.toml')

    completed = subprocess.run(
        ['git', 'show', '$PYPROJECT'],  # noqa: S607
        check=False,
        capture_output=True,
        env={'PYPROJECT': safe_pyproject},
    )

    if completed.returncode != 0:
        return None

    return project_version(tomllib.loads(completed.stdout.decode()))


def is_prerelease(value: str) -> bool:
    return re.search(r'(?:a|b|rc)\d+|\.dev\d+', value, re.IGNORECASE) is not None


def write_output(name: str, value: str) -> None:
    output_path = os.environ.get('GITHUB_OUTPUT')
    if output_path:
        with Path(output_path).open('a', encoding='utf-8') as file:
            file.write(f'{name}={value}\n')


def main() -> int:
    arguments = parse_arguments()
    current = current_version()
    previous = previous_version(arguments.before)
    changed = arguments.force or previous != current
    tag = f'v{current}'
    prerelease = is_prerelease(current)

    outputs = {
        'changed': str(changed).lower(),
        'prerelease': str(prerelease).lower(),
        'previous-version': previous or '',
        'tag': tag,
        'version': current,
    }

    for name, value in outputs.items():
        write_output(name, value)

    output_content = '\n'.join([
        f'previous version: {previous or "<unavailable>"}'
        f'current version: {current}'
        f'release needed: {str(changed).lower()}'
        f'release tag: {tag}'
    ])

    if step_summary := os.getenv('GITHUB_STEP_SUMMARY'):
        Path(step_summary).write_text(output_content)

    print(f'::notice::{output_content}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
