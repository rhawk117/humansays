import sys
from collections.abc import Sequence
from typing import TextIO

from humansays.config.loading import ConfigError, load_settings
from humansays.const import CONFIG_ERROR_EXIT


def main(argv: Sequence[str] | None = None, stream: TextIO | None = None) -> int:
    try:
        load_settings(argv)
    except ConfigError as err:
        print(f'error: config file not found: {err.path}', file=sys.stderr)
        return CONFIG_ERROR_EXIT
    # real body in Task B12
    raise NotImplementedError
