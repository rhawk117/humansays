import ast
from pathlib import Path

from .models import ParsedModule
from .rules import RulesetEvaluator

__all__ = ('RulesetEvaluator', 'parse_module')


def parse_module(path: Path) -> ParsedModule:
    source = path.read_text(encoding='utf-8')
    tree = ast.parse(source, filename=str(path))
    return ParsedModule(path, source, tree)
