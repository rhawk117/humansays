import ast
from pathlib import Path

from humansays.analysis.extraction import extract
from humansays.analysis.models import ParsedModule

__all__ = ('extract', 'parse_module')


def parse_module(path: Path) -> ParsedModule:
    source = path.read_text(encoding='utf-8')
    tree = ast.parse(source, filename=str(path))
    return ParsedModule(path, source, tree)
