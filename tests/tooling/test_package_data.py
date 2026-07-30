"""Rule definitions are package data, and package data is easy to lose.

`pyproject.toml` carries no `[tool.uv.build-backend]` section, so whether
`uv_build` ships `*.toml` under `src/` is a default, not a declaration. A
default that changes breaks the installed package only -- the source tree keeps
working, every other test keeps passing, and the failure surfaces after
publish. This builds a real wheel and loads every group out of a real install.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from humansays.rules.loading import GROUPS

REPO_ROOT = Path(__file__).resolve().parents[2]

# Loads through importlib.resources the same way humansays.rules.loading does,
# but against the installed package rather than the source tree.
LOAD_SCRIPT = """
import tomllib
from importlib.resources import files

groups = {groups!r}
for group in groups:
    document = tomllib.loads(
        files('humansays.rules').joinpath(group, 'rules.toml').read_text('utf-8')
    )
    assert document['rule'], group

print(sum(len(tomllib.loads(
    files('humansays.rules').joinpath(g, 'rules.toml').read_text('utf-8')
)['rule']) for g in groups))
"""


@pytest.fixture(scope='module')
def wheel(tmp_path_factory: pytest.TempPathFactory) -> Path:
    assert shutil.which('uv'), 'uv is required to build the wheel'
    destination = tmp_path_factory.mktemp('dist')
    subprocess.run(  # noqa: S603
        ['uv', 'build', '--wheel', '--out-dir', str(destination)],  # noqa: S607
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    built = sorted(destination.glob('*.whl'))
    assert len(built) == 1, f'expected one wheel, got {built}'
    return built[0]


def test_wheel_carries_every_group_definition(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        shipped = {name for name in archive.namelist() if name.endswith('rules.toml')}

    expected = {f'humansays/rules/{group}/rules.toml' for group in GROUPS}
    assert shipped == expected


def test_installed_package_loads_every_group(wheel: Path, tmp_path: Path) -> None:
    venv = tmp_path / 'venv'
    subprocess.run(  # noqa: S603
        ['uv', 'venv', str(venv)],  # noqa: S607
        check=True,
        capture_output=True,
    )
    subprocess.run(  # noqa: S603
        ['uv', 'pip', 'install', '--python', str(venv), str(wheel)],  # noqa: S607
        check=True,
        capture_output=True,
    )
    interpreter = venv / (
        'Scripts/python.exe' if sys.platform == 'win32' else 'bin/python'
    )
    completed = subprocess.run(  # noqa: S603
        [str(interpreter), '-c', LOAD_SCRIPT.format(groups=GROUPS)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.strip() == '19'
