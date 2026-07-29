"""Compatibility shim over extraction plus evaluation.

The rules moved to ``humansays.signals``. This keeps ``RulesetEvaluator``
alive for one commit so the golden gates verify the split in isolation.
"""

from humansays.analysis.extraction import extract
from humansays.analysis.models import AnalysisIndex, MutationVocabulary, ParsedModule
from humansays.config.models import Thresholds
from humansays.findings.models import Finding
from humansays.signals.evaluation import evaluate


class RulesetEvaluator:
    def __init__(
        self,
        module: ParsedModule,
        thresholds: Thresholds,
        vocabulary: MutationVocabulary = MutationVocabulary(),  # noqa: B008 -- frozen, safe to share
    ) -> None:
        self.facts = extract(module, vocabulary)
        self.thresholds = thresholds

    @property
    def index(self) -> AnalysisIndex:
        return AnalysisIndex(
            symbols=set(self.facts.symbols),
            functions=list(self.facts.all_functions),
            classes={item.name: list(item.methods) for item in self.facts.classes},
        )

    def run(self) -> list[Finding]:
        return evaluate(self.facts, self.thresholds)
