import sys
from collections.abc import Sequence
from typing import TextIO

from humansays import application
from humansays.config.loading import ConfigError, load_settings
from humansays.const import CONFIG_ERROR_EXIT, MISSING_SYMBOL_EXIT, NO_FILES_EXIT
from humansays.reporting.models import ReportRequest
from humansays.reporting.render import write_report
from humansays.scoring import score_for


def main(argv: Sequence[str] | None = None, stream: TextIO | None = None) -> int:
    try:
        settings = load_settings(argv)
    except ConfigError as err:
        print(f'error: config file not found: {err.path}', file=sys.stderr)
        return CONFIG_ERROR_EXIT

    specs = application.resolve_specs(settings.selection, stream or sys.stdin)
    paths = application.collect_files(specs, settings.selection.excludes)
    if not paths:
        source = ', '.join(specs) or '<stdin>'
        print(f'error: no Python files found in {source}', file=sys.stderr)
        return NO_FILES_EXIT

    result = application.analyze_paths(paths, settings)
    wanted = settings.selection.symbol

    if wanted and not application.symbol_is_present(result, wanted):
        print(f'error: symbol {wanted!r} not found', file=sys.stderr)
        return MISSING_SYMBOL_EXIT

    score = score_for(result)
    code = application.exit_code(result, score, settings)
    write_report(ReportRequest(result, score, settings.report, code))
    return code
