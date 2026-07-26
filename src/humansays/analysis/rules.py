"""Signal rules: turn extracted facts into findings.

``cpython_ast`` owns the AST vocabulary and fact extraction; this module owns
the judgement calls.

Known contract debt: this module still fuses ast-extraction (walking
``FunctionVisitor`` results, module scopes) with rule evaluation (weight,
severity, review question judgement calls). Splitting fact-extraction from
signal-evaluation into a dedicated ``humansays.signals`` layer is out of scope
for this migration -- see the plan's "Known contract debt" section -- so it
stays under ``analysis`` for now even though the evaluation half of it does not
strictly need ``ast``.
"""

import ast
from operator import attrgetter

from humansays.catalog import build_finding
from humansays.config.models import Thresholds
from humansays.const import (
    BOUNDARY_MINIMUM,
    COHESION_FIELD_MINIMUM,
    COHESION_METHOD_MINIMUM,
    MUTATION_OWNER_MINIMUM,
)
from humansays.enums import SignalName
from humansays.findings.models import Finding, Location, Observation

from .cpython_ast import (
    FUNCTION_NODES,
    FunctionVisitor,
    attribute_prefix_clusters,
    build_signature,
    collect_aliases,
    collect_module_globals,
    declared_class_attributes,
    is_trivial_accessor,
    module_scale_findings,
)
from .models import (
    AnalysisIndex,
    FunctionFacts,
    FunctionNode,
    MutationVocabulary,
    ParsedModule,
    Scope,
    ScopeContext,
)
from .syntax import (
    assigned_names,
    code_line_count,
    decorator_names,
    dotted_name,
    is_mutable_expression,
    location_of,
    node_span,
    snippet,
)

STATIC_DECORATOR = 'staticmethod'


class Analyzer:
    def __init__(
        self,
        module: ParsedModule,
        thresholds: Thresholds,
        vocabulary: MutationVocabulary = MutationVocabulary(),  # noqa: B008 -- frozen, safe to share
    ) -> None:
        self.module = module
        self.thresholds = thresholds
        self.context = ScopeContext(
            aliases=collect_aliases(module.tree),
            module_globals=collect_module_globals(module.tree),
            vocabulary=vocabulary,
        )
        self.findings: list[Finding] = []
        self.index = AnalysisIndex()
        span = max(1, len(module.lines))
        self.index.add_scope(Scope(module.tree, '<module>', 1, span))

    def run(self) -> list[Finding]:
        self.findings.extend(
            module_scale_findings(self.module, self.thresholds.modules),
        )
        self._mutable_bindings(self.module.tree.body, '<module>', 'module')
        for node in self.module.tree.body:
            if isinstance(node, FUNCTION_NODES):
                self._analyze_function(node, node.name)
            elif isinstance(node, ast.ClassDef):
                self._analyze_class(node)
        self._lambda_signals()
        return sorted(self.findings, key=attrgetter('sort_key'))

    def _record(
        self,
        signal: SignalName,
        location: Location,
        observation: Observation,
    ) -> None:
        self.findings.append(build_finding(signal, location, observation))

    def _analyze_class(self, node: ast.ClassDef) -> None:
        self.index.add_scope(Scope(node, node.name, *node_span(node)))
        self._mutable_bindings(node.body, node.name, 'class')
        self._base_classes(node)
        methods: list[FunctionFacts] = []
        for child in node.body:
            if isinstance(child, FUNCTION_NODES):
                name = f'{node.name}.{child.name}'
                methods.append(self._analyze_function(child, name, node.name))
                self._static_method(child, name)
        self.index.classes[node.name] = methods
        self._class_state_surface(node, methods)
        self._class_cohesion(node, methods)

    def _analyze_function(
        self,
        node: FunctionNode,
        qualified_name: str,
        class_name: str | None = None,
    ) -> FunctionFacts:
        signature = build_signature(node)
        visitor = FunctionVisitor(signature.parameters, self.context)
        for statement in node.body:
            visitor.visit(statement)
        visitor.body.code_lines = code_line_count(self.module, node)

        facts = FunctionFacts(
            location=location_of(qualified_name, node),
            class_name=class_name,
            signature=type(signature)(
                parameters=signature.parameters,
                boolean_parameters=signature.boolean_parameters,
                validated_parameters=dict(visitor.validated),
            ),
            body=visitor.body,
            self_usage=visitor.usage,
            trivial_accessor=is_trivial_accessor(node),
        )
        self.index.functions.append(facts)
        self.index.add_scope(
            Scope(node, qualified_name, facts.location.line, facts.location.end_line),
        )
        self._argument_signals(facts)
        self._size_signals(facts)
        self._control_flow_signals(facts)
        self._incident_signals(facts)
        self._state_signals(facts)
        return facts

    def _static_method(self, node: FunctionNode, qualified_name: str) -> None:
        """HS015: a staticmethod is a module function wearing a class as a namespace."""
        if STATIC_DECORATOR not in decorator_names(node):
            return
        observation = Observation(
            'Method is declared @staticmethod, so it can reach neither instance '
            'nor class state.',
            (f'line {node.lineno}: @staticmethod {node.name}',),
        )
        self._record(SignalName.HS015, location_of(qualified_name, node), observation)

    def _lambda_signals(self) -> None:
        """HS016: lambdas are anonymous, unimportable, and awkward to test."""
        for node in ast.walk(self.module.tree):
            if not isinstance(node, ast.Lambda):
                continue
            scope = self.index.scope_for_line(node.lineno)
            observation = Observation(
                'Lambda expression stands in for a named function.',
                (f'line {node.lineno}: {snippet(node)}',),
            )
            self._record(SignalName.HS016, location_of(scope.symbol, node), observation)

    def _base_classes(self, node: ast.ClassDef) -> None:
        """HS018: multiple parents make the method resolution order the real design."""
        bases = tuple(dotted_name(base) or snippet(base) for base in node.bases)
        if len(bases) <= self.thresholds.classes.max_base_classes:
            return
        observation = Observation(
            f'Class inherits from {len(bases)} parent classes.',
            bases,
        )
        self._record(SignalName.HS018, location_of(node.name, node), observation)

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
        body: list[ast.stmt],
        symbol: str,
        scope: str,
    ) -> None:
        constructors = self.context.vocabulary.constructors
        for statement in body:
            if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
                continue
            for name, value in assigned_names(statement):
                if not is_mutable_expression(value, self.context.aliases, constructors):
                    continue
                line, end_line = node_span(statement)
                self._record(
                    SignalName.HS004,
                    Location(symbol, line, end_line),
                    Observation(
                        f'Mutable {scope}-scope state `{name}` is shared beyond '
                        'one instance or operation.',
                        (f'{name} initialized as {type(value).__name__}',),
                    ),
                )

    def _class_state_surface(
        self,
        node: ast.ClassDef,
        methods: list[FunctionFacts],
    ) -> None:
        attributes = declared_class_attributes(node) | {
            attribute
            for method in methods
            for attribute in method.self_usage.fields_written
        }
        if len(attributes) <= self.thresholds.classes.max_attributes:
            return
        location = location_of(node.name, node)
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

    def _class_cohesion(
        self,
        node: ast.ClassDef,
        methods: list[FunctionFacts],
    ) -> None:
        eligible = cohesion_candidates(methods)
        fields = {name for method in eligible for name in method_fields(method)}
        if (
            len(eligible) < COHESION_METHOD_MINIMUM
            or len(fields) < COHESION_FIELD_MINIMUM
        ):
            return
        usage = [method_fields(method) for method in eligible]
        components = connected_components(usage)
        if len(components) < 2:
            return
        evidence = []
        for component in components:
            names = [eligible[index].name for index in component]
            used = sorted(set().union(*(usage[index] for index in component)))
            evidence.append(f'methods {names} use fields {used}')
        self._record(
            SignalName.HS008,
            location_of(node.name, node),
            Observation(
                f'Class methods form {len(components)} disconnected '
                'field-access clusters.',
                tuple(evidence),
            ),
        )


def method_fields(method: FunctionFacts) -> set[str]:
    return method.self_usage.fields_read | method.self_usage.fields_written


def cohesion_candidates(methods: list[FunctionFacts]) -> list[FunctionFacts]:
    names = {method.name for method in methods}
    for method in methods:
        non_fields = names | method.self_usage.methods_called
        method.self_usage.fields_read -= non_fields
        method.self_usage.fields_written -= non_fields
    return [
        method
        for method in methods
        if not method.trivial_accessor
        and method.name != '__init__'
        and method_fields(method)
    ]


def connected_components(usage: list[set[str]]) -> list[list[int]]:
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
