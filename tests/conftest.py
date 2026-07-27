"""Suite-wide configuration.

Every test carries exactly one scope marker, applied from its top-level
directory rather than by decorator, so a test cannot be filed in a directory
and silently miss its marker.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest_plugins = [
    'tests.fixtures.paths',
    'tests.fixtures.modules',
    'tests.fixtures.environment',
]

_TESTS_ROOT = Path(__file__).resolve().parent

_MARKER_BY_DIRECTORY = {
    'unit': 'unit',
    'integration': 'integration',
    'tooling': 'tooling',
    'golden': 'integration',
}


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Mark every collected test according to the directory holding it."""
    del config
    for item in items:
        relative = Path(item.path).resolve().relative_to(_TESTS_ROOT)
        directory = relative.parts[0]
        marker = _MARKER_BY_DIRECTORY.get(directory)
        if marker is None:
            raise pytest.UsageError(
                f'{relative} is not under a directory with a scope marker; '
                f'expected one of {sorted(_MARKER_BY_DIRECTORY)}'
            )
        item.add_marker(marker)
