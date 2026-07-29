"""Signal rules: turn extracted facts into findings.

``extraction`` walks the tree and returns facts; this module owns the
judgement calls, meaning which threshold a fact has to cross and what the
resulting finding says. It reads no ast node.
"""

from operator import attrgetter

from humansays.analysis.extraction import extract
from humansays.analysis.models import AnalysisIndex, MutationVocabulary, ParsedModule
from humansays.analysis.python_ast import (
    attribute_prefix_clusters,
    module_scale_findings,
)
from humansays.catalog import build_finding
from humansays.config.models import Thresholds
from humansays.const import (
    BOUNDARY_MINIMUM,
    COHESION_FIELD_MINIMUM,
    COHESION_METHOD_MINIMUM,
    MUTATION_OWNER_MINIMUM,
)
from humansays.enums import SignalName
from humansays.facts.module import ClassFacts
from humansays.facts.values import FunctionFacts, MutableBinding
from humansays.findings.models import Finding, Location, Observation


class RulesetEvaluator:
    def __init__(
        self,
        module: ParsedModule,
        thresholds: Thresholds,
        vocabulary: MutationVocabulary = MutationVocabulary(),  # noqa: B008 -- frozen, safe to share
    ) -> None:
        self.facts = extract(module, vocabulary)
        self.thresholds = thresholds
        self.findings: list[Finding] = []

    @property
    def index(self) -> AnalysisIndex:
        return AnalysisIndex(
            symbols=set(self.facts.symbols),
            functions=list(self.facts.all_functions),
            classes={item.name: list(item.methods) for item in self.facts.classes},
        )

    def run(self) -> list[Finding]:
        self.findings.extend(
            module_scale_findings(self.facts.line_count, self.thresholds.modules),
        )
        self._mutable_bindings(self.facts.bindings, '<module>', 'module')
        for facts in self.facts.functions:
            self._evaluate_function(facts)

        for item in self.facts.classes:
            self._evaluate_class(item)

        self._lambda_signals()
        return sorted(self.findings, key=attrgetter('sort_key'))

    def _record(
        self,
        signal: SignalName,
        location: Location,
        observation: Observation,
    ) -> None:
        self.findings.append(build_finding(signal, location, observation))

    def _evaluate_class(self, item: ClassFacts) -> None:
        self._mutable_bindings(item.bindings, item.name, 'class')
        self._base_classes(item)
        for method in item.methods:
            self._evaluate_function(method)
            self._static_method(method)

        self._class_state_surface(item)
        self._class_cohesion(item)

    def _evaluate_function(self, facts: FunctionFacts) -> None:
        self._argument_signals(facts)
        self._size_signals(facts)
        self._control_flow_signals(facts)
        self._incident_signals(facts)
        self._state_signals(facts)

    def _static_method(self, facts: FunctionFacts) -> None:
        """HS015: a staticmethod is a module function wearing a class as a namespace."""
        if not facts.static_method:
            return

        observation = Observation(
            'Method is declared @staticmethod, so it can reach neither instance '
            'nor class state.',
            (f'line {facts.location.line}: @staticmethod {facts.name}',),
        )

        self._record(SignalName.HS015, facts.location, observation)

    def _lambda_signals(self) -> None:
        """HS016: lambdas are anonymous, unimportable, and awkward to test."""
        for site in self.facts.lambdas:
            observation = Observation(
                'Lambda expression stands in for a named function.',
                (f'line {site.line}: {site.source}',),
            )
            self._record(
                SignalName.HS016,
                Location(site.symbol, site.line, site.line),
                observation,
            )

    def _base_classes(self, item: ClassFacts) -> None:
        """HS018: multiple parents make the method resolution order the real design."""
        bases = item.base_classes
        if len(bases) <= self.thresholds.classes.max_base_classes:
            return

        observation = Observation(
            f'Class inherits from {len(bases)} parent classes.',
            bases,
        )
        self._record(SignalName.HS018, item.location, observation)

    def _argument_signals(self, facts: FunctionFacts) -> None:
        signature = facts.signature
        operation = signature.operation_parameters
        if len(operation) > self.thresholds.functions.max_arguments:
            self._record(
                SignalName.HS001,
                facts.location,
                Observation(
                    f'Function accepts {len(operation)} operation arguments.',
                    operation,
                ),
            )
            self._validated_bundle(facts)

        booleans = signature.operation_booleans
        setter = facts.name.startswith('set_') and len(operation) == 1
        if booleans and not setter:
            self._record(
                SignalName.HS002,
                facts.location,
                Observation(
                    'Boolean parameters select behavior or operating modes.',
                    booleans,
                ),
            )

    def _validated_bundle(self, facts: FunctionFacts) -> None:
        validated = facts.signature.validated_parameters
        names = tuple(
            parameter
            for parameter in facts.signature.operation_parameters
            if parameter in validated
        )

        if not names:
            return

        evidence = tuple(
            f'{parameter}: {min(validated[parameter])}' for parameter in names
        )

        self._record(
            SignalName.HS014,
            facts.location,
            Observation(
                f'Function validates {len(names)} of its argument bundle internally.',
                evidence,
            ),
        )

    def _size_signals(self, facts: FunctionFacts) -> None:
        limits = self.thresholds.functions
        if facts.length > limits.max_lines:
            self._record(
                SignalName.HS009,
                facts.location,
                Observation(
                    f'Function spans {facts.length} source lines.',
                    (f'configured threshold: {limits.max_lines}',),
                ),
            )

        if facts.body.code_lines > limits.max_code_lines:
            self._record(
                SignalName.HS022,
                facts.location,
                Observation(
                    f'Function holds {facts.body.code_lines} lines of code.',
                    (
                        f'configured threshold: {limits.max_code_lines}',
                        'blank lines, comments, and the docstring are excluded',
                    ),
                ),
            )

    def _control_flow_signals(self, facts: FunctionFacts) -> None:
        limits = self.thresholds.functions
        limit = limits.nesting_limit(facts.class_name)
        if facts.body.maximum_nesting > limit:
            evidence = [f'configured threshold: {limit}']
            if facts.class_name:
                evidence.append(
                    f'class bodies receive +{limits.class_nesting_bonus} nesting',
                )

            self._record(
                SignalName.HS003,
                facts.location,
                Observation(
                    f'Control flow reaches nesting depth {facts.body.maximum_nesting}.',
                    tuple(evidence),
                ),
            )
        if facts.body.branches > limits.max_branches:
            self._record(
                SignalName.HS019,
                facts.location,
                Observation(
                    f'Function contains {facts.body.branches} if/elif statements.',
                    (f'configured threshold: {limits.max_branches}',),
                ),
            )

    def _incident_signals(self, facts: FunctionFacts) -> None:
        messages = {
            SignalName.HS005: 'Broad exception handling may collapse unrelated failures.',
            SignalName.HS021: 'Import is deferred into the function body.',
        }

        for signal, incidents in facts.body.incidents.items():
            for incident in incidents:
                self._record(
                    signal,
                    facts.location,
                    Observation(
                        messages[signal],
                        (f'line {incident.line}: {incident.detail}',),
                    ),
                )

    def _state_signals(self, facts: FunctionFacts) -> None:
        mutations = facts.body.mutations
        if len(mutations) >= MUTATION_OWNER_MINIMUM:
            evidence = tuple(
                f'{owner}: {min(details)}' for owner, details in sorted(mutations.items())
            )
            self._record(
                SignalName.HS006,
                facts.location,
                Observation(
                    f'Function appears to mutate {len(mutations)} independent '
                    'state owners.',
                    evidence,
                ),
            )
        boundaries = facts.body.boundaries
        if len(boundaries) >= BOUNDARY_MINIMUM:
            evidence = tuple(
                f'{boundary}: {min(details)}'
                for boundary, details in sorted(boundaries.items())
            )
            self._record(
                SignalName.HS007,
                facts.location,
                Observation(
                    f'Function uses {len(boundaries)} standard-library boundary '
                    'categories.',
                    evidence,
                ),
            )

    def _mutable_bindings(
        self,
        bindings: tuple[MutableBinding, ...],
        symbol: str,
        scope: str,
    ) -> None:
        for binding in bindings:
            self._record(
                SignalName.HS004,
                Location(symbol, binding.line, binding.end_line),
                Observation(
                    f'Mutable {scope}-scope state `{binding.name}` is shared beyond '
                    'one instance or operation.',
                    (f'{binding.name} initialized as {binding.constructor}',),
                ),
            )

    def _class_state_surface(self, item: ClassFacts) -> None:
        attributes = item.state_attributes
        if len(attributes) <= self.thresholds.classes.max_attributes:
            return
        location = item.location
        self._record(
            SignalName.HS012,
            location,
            Observation(
                f'Class owns {len(attributes)} state attributes.',
                tuple(sorted(attributes)),
            ),
        )
        clusters = attribute_prefix_clusters(attributes)
        if clusters:
            evidence = tuple(
                f'{prefix}_*: {", ".join(names)}'
                for prefix, names in sorted(clusters.items())
            )
            self._record(
                SignalName.HS013,
                location,
                Observation(
                    f'Large class contains {len(clusters)} repeated '
                    'attribute-prefix clusters.',
                    evidence,
                ),
            )

    def _class_cohesion(self, item: ClassFacts) -> None:
        eligible = cohesion_candidates(list(item.methods))
        usage = [fields for _, fields in eligible]
        fields = {name for group in usage for name in group}
        if (
            len(eligible) < COHESION_METHOD_MINIMUM
            or len(fields) < COHESION_FIELD_MINIMUM
        ):
            return
        components = connected_components(usage)
        if len(components) < 2:
            return
        evidence = []
        for component in components:
            names = [eligible[index][0].name for index in component]
            used = sorted(set().union(*(usage[index] for index in component)))
            evidence.append(f'methods {names} use fields {used}')
        self._record(
            SignalName.HS008,
            item.location,
            Observation(
                f'Class methods form {len(components)} disconnected '
                'field-access clusters.',
                tuple(evidence),
            ),
        )


def field_usage(method: FunctionFacts, method_names: frozenset[str]) -> frozenset[str]:
    non_fields = method_names | method.self_usage.methods_called
    fields = method.self_usage.fields_read | method.self_usage.fields_written
    return fields - non_fields


def cohesion_candidates(
    methods: list[FunctionFacts],
) -> list[tuple[FunctionFacts, frozenset[str]]]:
    method_names = frozenset(method.name for method in methods)
    candidates = (
        (method, field_usage(method, method_names))
        for method in methods
        if not method.trivial_accessor and method.name != '__init__'
    )
    return [(method, fields) for method, fields in candidates if fields]


def connected_components(usage: list[frozenset[str]]) -> list[list[int]]:
    remaining = set(range(len(usage)))
    components: list[list[int]] = []
    while remaining:
        component = {remaining.pop()}
        additions = {0}
        while additions:
            shared: set[str] = set().union(*(usage[index] for index in component))
            additions = {index for index in remaining if shared & usage[index]}
            component |= additions
            remaining -= additions

        components.append(sorted(component))

    return components
