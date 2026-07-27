"""A TOML config is UTF-8 whatever the machine's locale says.

`toml_values` reads in binary mode and lets `tomllib` decode, because TOML is
UTF-8 by specification. Reading the file as text first would decode with the
locale encoding, which mis-decodes a non-ASCII config on a machine that is not
set to UTF-8.

These do not reproduce that failure: pytest runs under whatever locale the host
has, and forcing a different one mid-process is not portable. They pin the
UTF-8 path and the binary read instead.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

from humansays.config.loading import toml_values

if TYPE_CHECKING:
    from pathlib import Path

NON_ASCII_PATTERN = 'genéré/*'


def test_non_ascii_values_survive_a_round_trip(tmp_path: Path) -> None:
    config = tmp_path / 'humansays.toml'
    config.write_bytes(f'[selection]\nexclude = ["{NON_ASCII_PATTERN}"]\n'.encode())

    assert toml_values(config) == {'selection': {'exclude': [NON_ASCII_PATTERN]}}


def test_non_ascii_values_survive_a_pyproject_round_trip(tmp_path: Path) -> None:
    config = tmp_path / 'pyproject.toml'
    config.write_bytes(
        f'[tool.humansays.selection]\nexclude = ["{NON_ASCII_PATTERN}"]\n'.encode()
    )

    assert toml_values(config) == {'selection': {'exclude': [NON_ASCII_PATTERN]}}


def test_the_file_is_read_as_bytes() -> None:
    """Guards the decision, not just its result, since the host locale is UTF-8.

    `read_text` without an explicit encoding is the specific mistake this
    replaced, and it passes every assertion above on a UTF-8 machine.
    """
    code = [
        line
        for line in inspect.getsource(toml_values).splitlines()
        if not line.lstrip().startswith('#')
    ]

    assert any("path.open('rb')" in line for line in code)
    assert not any('read_text' in line for line in code)
