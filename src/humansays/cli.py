import argparse
import contextlib
import logging
import os
import sys
import traceback
from collections.abc import Iterator, Sequence
from typing import TextIO

from humansays import application
from humansays.config.loading import ConfigError, load_settings
from humansays.const import (
    CONFIG_ERROR_EXIT,
    INTERNAL_ERROR_EXIT,
    MISSING_SYMBOL_EXIT,
    NO_FILES_EXIT,
    NO_FILES_TEMPLATE,
    NO_PATHS_MESSAGE,
)
from humansays.reporting.console import Console
from humansays.reporting.models import ReportRequest
from humansays.reporting.render import write_report
from humansays.scoring import score_for

LOG_LEVELS = (logging.ERROR, logging.INFO, logging.DEBUG)
LOG_FORMAT = 'humansays: %(levelname)s %(message)s'


def _verbosity(argv: Sequence[str] | None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-v', '--verbose', action='count', default=0)
    try:
        namespace, _ = parser.parse_known_args(argv)
    except SystemExit:
        return 0

    return namespace.verbose


@contextlib.contextmanager
def _diagnostics(verbosity: int) -> Iterator[None]:
    logger = logging.getLogger('humansays')
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    previous_level = logger.level
    logger.setLevel(LOG_LEVELS[min(verbosity, len(LOG_LEVELS) - 1)])
    logger.addHandler(handler)
    try:
        yield
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)
        handler.close()


def _run(argv: Sequence[str] | None, stream: TextIO | None, console: Console) -> int:
    settings = load_settings(argv)

    source_stream = stream or sys.stdin
    if not settings.selection.paths and source_stream.isatty():
        console.message(NO_PATHS_MESSAGE)
        return NO_FILES_EXIT

    specs = application.resolve_specs(settings.selection, source_stream)
    paths = application.collect_files(specs, settings.selection.excludes)
    logging.getLogger(__name__).info(
        'collected %d files from %s', len(paths), ', '.join(specs) or '<stdin>'
    )
    if not paths:
        source = ', '.join(specs) or '<stdin>'
        console.message(NO_FILES_TEMPLATE.format(source=source))
        return NO_FILES_EXIT

    result = application.analyze_paths(paths, settings)
    wanted = settings.selection.symbol

    if wanted and not application.symbol_is_present(result, wanted):
        console.message(f'error: symbol {wanted!r} not found')
        return MISSING_SYMBOL_EXIT

    score = score_for(result)
    code = application.exit_code(result, score, settings)
    write_report(ReportRequest(result, score, settings.report, code), console)
    return code


def main(argv: Sequence[str] | None = None, stream: TextIO | None = None) -> int:
    """Entry point. Every failure leaves here as an exit code, never a traceback."""
    console = Console(os.environ)
    with _diagnostics(_verbosity(argv)):
        try:
            return _run(argv, stream, console)
        except ConfigError as err:
            console.message(f'error: {err}')
            return CONFIG_ERROR_EXIT
        except Exception:  # noqa: BLE001
            console.message('internal error: this is a humansays bug')
            console.message(traceback.format_exc().rstrip('\n'))
            return INTERNAL_ERROR_EXIT
