# Source-accountability ledger

Extracted verbatim from NEW_RULES.md lines 464-679. Unpublished: this
is migration provenance, not product documentation.

## 9. Full source-accountability ledger

This ledger is deliberately exhaustive: 189 source signals plus 20 source findings are mapped below.

| Source ID | Source name | Disposition | Final/internal ID | Reason |
|---|---|---|---|---|
| HS-ARGS-01 | many-operation-arguments | on | CONTRACT003 | Retained as an independently selectable rule. |
| HS-ARGS-02 | positional-boolean | evidence | contract.positional_boolean | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-ARGS-03 | boolean-mode-switch | on | KISS003 | Retained as an independently selectable rule. |
| HS-ARGS-04 | data-clump | evidence | coup.data_clump | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-ARGS-05 | dependency-as-argument | omitted | — | Passing a dependency explicitly is normally healthier than hiding it in ambient state, so the original rule would push design in the wrong direction. |
| HS-ARGS-06 | optional-not-keyword-only | on | CONTRACT004 | Retained as an independently selectable rule. |
| HS-ARGS-07 | parameter-bag | evidence | coup.parameter_bag | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-ARGS-08 | untyped-varkwargs | external | — | Untyped `**kwargs` is directly covered by Ruff ANN003 and type checkers without a meaningful structural extension. |
| HS-ARGS-09 | mutually-exclusive-flags | on | CONTRACT005 | Retained as an independently selectable rule. |
| HS-ARGS-10 | single-attribute-dependency | on | COUP008 | Retained as an independently selectable rule. |
| HS-ARGS-11 | optional-argument-state-product | on | STATE018 | Retained as an independently selectable rule. |
| HS-ARGS-12 | none-as-command | on | POLA005 | Retained as an independently selectable rule. |
| HS-CLASS-01 | low-field-cohesion | on | SRP005 | Retained as an independently selectable rule. |
| HS-CLASS-02 | many-public-methods | evidence | srp.many_public_methods | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-CLASS-03 | many-class-attributes | evidence | srp.many_class_attributes | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-CLASS-04 | many-private-helpers | evidence | srp.many_private_helpers | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-CLASS-05 | attribute-prefix-cluster | evidence | srp.attribute_prefix_cluster | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-CLASS-06 | zero-state-namespace | hint | NIT002 | Retained as an independently selectable rule. |
| HS-CLASS-07 | stateless-single-method | hint | NIT003 | Retained as an independently selectable rule. |
| HS-CLASS-08 | many-base-classes | evidence | srp.many_base_classes | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-CLASS-09 | lsp-signature-drift | external | — | Override signature compatibility is already checked precisely by type checkers, while behavioral substitutability cannot be established from signatures alone. |
| HS-CLASS-10 | god-constructor | on | SRP006 | Retained as an independently selectable rule. |
| HS-CLASS-11 | abc-as-interface | hint | NIT020 | Retained as an independently selectable rule. |
| HS-CLASS-12 | protocol-not-runtime-checkable | on | IDIOM013 | Retained as an independently selectable rule. |
| HS-CLASS-13 | generic-arity-high | evidence | contract.generic_arity_high | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-CLASS-14 | private-method-count-high | evidence | srp.private_method_count_high | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-CLASS-15 | custom-metaclass | on | IDIOM014 | Retained as an independently selectable rule. |
| HS-CLASS-16 | template-method-not-final | evidence | contract.template_method_not_final | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-CLASS-17 | non-obvious-arithmetic-overload | on | POLA006 | Retained as an independently selectable rule. |
| HS-CLASS-18 | name-mangled-member | hint | NIT021 | Retained as an independently selectable rule. |
| HS-CLASS-19 | name-mangled-shadow | on | IDIOM015 | Retained as an independently selectable rule. |
| HS-CONC-01 | shared-state-across-await | on | CONC001 | Retained as an independently selectable rule. |
| HS-CONC-02 | lock-held-across-await | on | CONC002 | Retained as an independently selectable rule. |
| HS-CONC-03 | blocking-call-in-async | on | CONC003 | Retained as an independently selectable rule. |
| HS-CONC-04 | concurrency-primitive-mismatch | on | CONC004 | Retained as an independently selectable rule. |
| HS-CONC-05 | detached-task | on | CONC005 | Retained as an independently selectable rule. |
| HS-CONC-06 | inconsistent-lock-order | on | CONC006 | Retained as an independently selectable rule. |
| HS-CONC-07 | race-or-deadlock-observed | observe | CONC007 | Retained as an independently selectable rule. |
| HS-CONC-08 | async-shared-scope-mutation | on | CONC008 | Retained as an independently selectable rule. |
| HS-CONC-09 | local-context-variable | on | IDIOM002 | Retained as an independently selectable rule. |
| HS-EFFECT-01 | effect-database | evidence | fail.effect_database | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-EFFECT-02 | effect-network | evidence | fail.effect_network | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-EFFECT-03 | effect-filesystem | evidence | fail.effect_filesystem | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-EFFECT-04 | effect-subprocess | evidence | fail.effect_subprocess | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-EFFECT-05 | effect-notification | evidence | fail.effect_notification | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-EFFECT-06 | mixed-effect-boundaries | evidence | srp.mixed_effect_boundaries | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-EFFECT-07 | effect-inside-branch | evidence | kiss.effect_inside_branch | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-EFFECT-08 | effect-between-mutations | on | FAIL001 | Retained as an independently selectable rule. |
| HS-EFFECT-09 | unordered-multi-effect | on | FAIL002 | Retained as an independently selectable rule. |
| HS-EFFECT-10 | effect-in-domain-type | on | SRP002 | Retained as an independently selectable rule. |
| HS-EFFECT-11 | effect-in-comprehension | on | KISS001 | Retained as an independently selectable rule. |
| HS-EFFECT-12 | dynamic-python-execution | external | — | Standalone `eval`/`exec` detection is already owned by Bandit/Ruff security rules; humansays may retain the effect fact for higher-order findings. |
| HS-EFFECT-13 | process-image-replacement | external | — | Standalone `os.exec*` detection is security and process-policy linting; humansays only needs it as an effect and lifecycle fact. |
| HS-EFFECT-14 | shell-command-execution | external | — | Shell execution and `shell=True` are already covered by Bandit's shell-injection checks, leaving no unique standalone humansays claim. |
| HS-EFFECT-15 | effectful-property | on | POLA001 | Retained as an independently selectable rule. |
| HS-EFFECT-16 | effectful-operator-overload | on | POLA004 | Retained as an independently selectable rule. |
| HS-FAIL-01 | broad-exception-swallowed | on | FAIL004 | Retained as an independently selectable rule. |
| HS-FAIL-02 | broad-exception-logged-only | evidence | fail.broad_exception_logged_only | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-FAIL-03 | broad-exception-reraised | evidence | fail.broad_exception_reraised | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-FAIL-04 | bare-except | external | — | Bare `except` is a conventional lint diagnostic already owned by Ruff/Pylint. |
| HS-FAIL-05 | absence-collapsed-into-failure | on | FAIL005 | Retained as an independently selectable rule. |
| HS-FAIL-06 | absence-not-modeled | external | — | A return annotation that omits `None` is type-checker territory; humansays only retains correlated evidence when distinct failure paths collapse into absence. |
| HS-FAIL-07 | exception-as-control-flow | hint | NIT005 | Retained as an independently selectable rule. |
| HS-FAIL-08 | retry-without-idempotence | on | FAIL006 | Retained as an independently selectable rule. |
| HS-FAIL-09 | error-message-only | on | FAIL007 | Retained as an independently selectable rule. |
| HS-FAIL-10 | finally-suppresses | external | — | Control flow in `finally` is already reported by Ruff B012 with no structural inference needed. |
| HS-FAIL-11 | handler-never-fires | omitted | — | A handler not firing during one observation window does not establish that it is unreachable or unnecessary. |
| HS-FAIL-12 | handler-over-broad-observed | hint | NIT006 | Retained as an independently selectable rule. |
| HS-FAIL-13 | exception-handler-fanout | on | KISS009 | Retained as an independently selectable rule. |
| HS-FIND-01 | mixed responsibilities | on | SRP003 | Retained as an independently selectable rule. |
| HS-FIND-02 | side-effect orchestration risk | on | FAIL008 | Retained as an independently selectable rule. |
| HS-FIND-03 | unclassifiable unit | on | SRP007 | Retained as an independently selectable rule. |
| HS-FIND-04 | missing state owner | on | STATE011 | Retained as an independently selectable rule. |
| HS-FIND-05 | incohesive class | on | SRP008 | Retained as an independently selectable rule. |
| HS-FIND-06 | control-flow pressure | on | KISS004 | Retained as an independently selectable rule. |
| HS-FIND-07 | ceremonial abstraction | hint | NIT013 | Retained as an independently selectable rule. |
| HS-FIND-08 | hidden dependency surface | on | COUP006 | Retained as an independently selectable rule. |
| HS-FIND-09 | untestable without environment | on | COUP007 | Retained as an independently selectable rule. |
| HS-FIND-10 | unprotected invariant | on | STATE012 | Retained as an independently selectable rule. |
| HS-FIND-11 | temporal coupling | on | LIFE007 | Retained as an independently selectable rule. |
| HS-FIND-12 | ambiguous failure contract | on | FAIL009 | Retained as an independently selectable rule. |
| HS-FIND-13 | silent infrastructure failure | on | FAIL010 | Retained as an independently selectable rule. |
| HS-FIND-14 | compensating commentary | hint | NIT014 | Retained as an independently selectable rule. |
| HS-FIND-15 | dead defensive structure | omitted | — | Runtime non-execution cannot justify the finding's claim that defensive structure is dead. |
| HS-FIND-16 | constructor is an operation | on | LIFE014 | Retained as an independently selectable rule. |
| HS-FIND-17 | async state has no task owner | on | CONC009 | Retained as an independently selectable rule. |
| HS-FIND-18 | type-contract friction | on | CONTRACT009 | Retained as an independently selectable rule. |
| HS-FIND-19 | destructive mutation hidden from caller | on | POLA007 | Retained as an independently selectable rule. |
| HS-FIND-20 | excessive representable state space | on | STATE001 | Retained as an independently selectable rule. |
| HS-INIT-01 | unvalidated-construction | evidence | life.unvalidated_construction | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-INIT-02 | post-construction-setup | on | LIFE003 | Retained as an independently selectable rule. |
| HS-INIT-03 | partial-init | on | STATE009 | Retained as an independently selectable rule. |
| HS-INIT-04 | invariant-bypass | on | STATE010 | Retained as an independently selectable rule. |
| HS-INIT-05 | missing-transition-method | replaced | — | The absence of a named transition method proves nothing, so it is replaced by a rule that requires repeated ad hoc state writes and transition guards. |
| HS-INIT-06 | exception-leaves-partial-state | on | FAIL003 | Retained as an independently selectable rule. |
| HS-INIT-07 | validated-argument-bundle | evidence | contract.validated_argument_bundle | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-INIT-08 | frozen-candidate | hint | NIT001 | Retained as an independently selectable rule. |
| HS-INIT-09 | equality-without-invariant | omitted | — | Defining equality does not imply that construction validation or a stronger invariant is required. |
| HS-INIT-10 | frozen-state-bypass | on | IDIOM010 | Retained as an independently selectable rule. |
| HS-INIT-11 | positional-dataclass-ambiguity | on | CONTRACT008 | Retained as an independently selectable rule. |
| HS-INIT-12 | missing-dataclass-slots | hint | NIT018 | Retained as an independently selectable rule. |
| HS-INIT-13 | concrete-factory-return | on | IDIOM011 | Retained as an independently selectable rule. |
| HS-INIT-14 | accidental-enum-values | evidence | idiom.accidental_enum_values | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-INIT-15 | overridable-call-during-init | on | LIFE011 | Retained as an independently selectable rule. |
| HS-INIT-16 | callback-during-construction | on | LIFE012 | Retained as an independently selectable rule. |
| HS-INIT-17 | self-escapes-before-invariant | on | LIFE013 | Retained as an independently selectable rule. |
| HS-INPUT-01 | env-read-in-logic | on | COUP002 | Retained as an independently selectable rule. |
| HS-INPUT-02 | clock-read-inline | on | COUP003 | Retained as an independently selectable rule. |
| HS-INPUT-03 | randomness-inline | on | COUP004 | Retained as an independently selectable rule. |
| HS-INPUT-04 | module-global-read | on | STATE002 | Retained as an independently selectable rule. |
| HS-INPUT-05 | module-global-write | on | STATE003 | Retained as an independently selectable rule. |
| HS-INPUT-06 | settings-singleton-access | on | COUP005 | Retained as an independently selectable rule. |
| HS-INPUT-07 | import-time-side-effect | on | LIFE001 | Retained as an independently selectable rule. |
| HS-INPUT-08 | constructor-does-work | on | LIFE002 | Retained as an independently selectable rule. |
| HS-INPUT-09 | dependency-count-high | evidence | coup.dependency_count_high | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-INPUT-10 | direct-environ-index | hint | NIT016 | Retained as an independently selectable rule. |
| HS-INPUT-11 | import-time-resource-construction | on | LIFE008 | Retained as an independently selectable rule. |
| HS-INPUT-12 | implicit-policy-dependency | evidence | coup.implicit_policy_dependency | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-INPUT-13 | import-path-mutation | on | IDIOM003 | Retained as an independently selectable rule. |
| HS-INPUT-14 | dynamic-namespace-access | on | IDIOM004 | Retained as an independently selectable rule. |
| HS-INPUT-15 | module-attribute-hook | on | IDIOM005 | Retained as an independently selectable rule. |
| HS-INPUT-16 | module-object-customization | on | IDIOM006 | Retained as an independently selectable rule. |
| HS-INPUT-17 | import-time-exit-hook | on | LIFE009 | Retained as an independently selectable rule. |
| HS-INPUT-18 | cached-singleton-factory | hint | NIT017 | Retained as an independently selectable rule. |
| HS-LEAK-01 | instance-growth | evidence | life.instance_growth | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-LEAK-02 | project-type-cycle | evidence | life.project_type_cycle | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-LEAK-03 | traceback-retention | observe | LIFE004 | Retained as an independently selectable rule. |
| HS-LEAK-04 | unbounded-container | evidence | life.unbounded_container | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-LEAK-05 | finalizer-dependent-release | observe | LIFE005 | Retained as an independently selectable rule. |
| HS-LEAK-06 | allocation-growth | evidence | life.allocation_growth | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-LEAK-07 | unbounded-cache | observe | LIFE006 | Retained as an independently selectable rule. |
| HS-NARRATION-01 | sectioning-comment | hint | NIT007 | Retained as an independently selectable rule. |
| HS-NARRATION-02 | restating-comment | hint | NIT008 | Retained as an independently selectable rule. |
| HS-NARRATION-03 | comment-density-high | hint | NIT009 | Retained as an independently selectable rule. |
| HS-NARRATION-04 | docstring-restates-signature | hint | NIT010 | Retained as an independently selectable rule. |
| HS-NARRATION-05 | commented-out-code | external | — | Commented-out code is directly covered by Ruff ERA001/eradicate-style checks and does not require correlated structural analysis. |
| HS-NARRATION-06 | todo-marker | hint | NIT011 | Retained as an independently selectable rule. |
| HS-NARRATION-07 | placeholder-implementation | hint | NIT012 | Retained as an independently selectable rule. |
| HS-NARRATION-08 | defensive-redundancy | replaced | — | The broad defensive-redundancy claim trusted annotations and observed call sites too much; it is replaced by the narrow numeric truthiness rule IDIOM008. |
| HS-NARRATION-09 | uniform-try-wrapping | off | DRY001 | Retained as an independently selectable rule. |
| HS-NARRATION-10 | over-parameterized-helper | off | DRY002 | Retained as an independently selectable rule. |
| HS-NARRATION-11 | symmetric-boilerplate | off | DRY003 | Retained as an independently selectable rule. |
| HS-NARRATION-12 | branch-never-taken | omitted | — | An untaken branch in one runtime sample is coverage evidence, not proof that the branch is dead. |
| HS-PURPOSE-01 | unclassifiable-role | evidence | srp.unclassifiable_role | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-PURPOSE-02 | command-query-violation | on | CQS001 | Retained as an independently selectable rule. |
| HS-PURPOSE-03 | query-performs-io | on | CQS002 | Retained as an independently selectable rule. |
| HS-PURPOSE-04 | generic-name | evidence | srp.generic_name | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-PURPOSE-05 | untyped-dict-parameter | on | CONTRACT001 | Retained as an independently selectable rule. |
| HS-PURPOSE-06 | untyped-dict-return | on | CONTRACT002 | Retained as an independently selectable rule. |
| HS-PURPOSE-07 | missing-return-annotation | external | — | Missing return annotations are owned by annotation linters and type checkers; humansays gains no structural inference by repeating the standalone diagnostic. |
| HS-PURPOSE-08 | conjunctive-name | evidence | srp.conjunctive_name | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-PURPOSE-09 | mutation-disguised-as-calculation | on | CQS003 | Retained as an independently selectable rule. |
| HS-PURPOSE-10 | role-conflict | on | SRP001 | Retained as an independently selectable rule. |
| HS-PURPOSE-11 | undeclared-dependency | on | COUP001 | Retained as an independently selectable rule. |
| HS-PURPOSE-12 | object-annotation | hint | NIT015 | Retained as an independently selectable rule. |
| HS-PURPOSE-13 | unchecked-any-operation | on | CONTRACT006 | Retained as an independently selectable rule. |
| HS-PURPOSE-14 | positional-record-return | on | CONTRACT007 | Retained as an independently selectable rule. |
| HS-PURPOSE-15 | representation-as-identity | on | POLA003 | Retained as an independently selectable rule. |
| HS-PURPOSE-16 | process-hash-as-identity | on | IDIOM001 | Retained as an independently selectable rule. |
| HS-SHAPE-01 | long-function | evidence | kiss.long_function | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-SHAPE-02 | dense-function | evidence | kiss.dense_function | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-SHAPE-03 | deep-nesting | evidence | kiss.deep_nesting | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-SHAPE-04 | many-branches | evidence | kiss.many_branches | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-SHAPE-05 | disjoint-local-clusters | evidence | srp.disjoint_local_clusters | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-SHAPE-06 | single-use-private-helper | evidence | kiss.single_use_private_helper | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-SHAPE-07 | helper-chain | on | KISS002 | Retained as an independently selectable rule. |
| HS-SHAPE-08 | narration-extraction | evidence | kiss.narration_extraction | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-SHAPE-09 | mixed-abstraction-levels | on | SRP004 | Retained as an independently selectable rule. |
| HS-SHAPE-10 | long-module | evidence | kiss.long_module | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-SHAPE-11 | literal-policy-iterable | evidence | kiss.literal_policy_iterable | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-SHAPE-12 | manual-dataclass-projection | off | DRY004 | Retained as an independently selectable rule. |
| HS-SHAPE-13 | long-loop-body | on | KISS005 | Retained as an independently selectable rule. |
| HS-SHAPE-14 | branch-pyramid | on | KISS006 | Retained as an independently selectable rule. |
| HS-SHAPE-15 | compound-domain-condition | on | KISS007 | Retained as an independently selectable rule. |
| HS-SHAPE-16 | nested-context-managers | hint | NIT019 | Retained as an independently selectable rule. |
| HS-SHAPE-17 | stdlib-idiom-reimplementation | on | IDIOM012 | Retained as an independently selectable rule. |
| HS-SHAPE-18 | repeated-type-or-value-dispatch | on | KISS008 | Retained as an independently selectable rule. |
| HS-STATE-01 | mutable-class-attribute | on | STATE004 | Retained as an independently selectable rule. |
| HS-STATE-02 | mutable-default-argument | external | — | Mutable argument defaults are a mature correctness check in Ruff B006 and need no higher-order humansays rule unless used as evidence of shared-state ownership. |
| HS-STATE-03 | leaked-internal-mutable | on | STATE005 | Retained as an independently selectable rule. |
| HS-STATE-04 | multiple-mutation-owners | evidence | state.multiple_mutation_owners | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-STATE-05 | caller-object-mutation | on | POLA002 | Retained as an independently selectable rule. |
| HS-STATE-06 | shared-mutable-binding | on | STATE006 | Retained as an independently selectable rule. |
| HS-STATE-07 | state-outlives-operation | evidence | state.state_outlives_operation | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-STATE-08 | generic-setter | evidence | state.generic_setter | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-STATE-09 | field-write-outside-owner | on | STATE007 | Retained as an independently selectable rule. |
| HS-STATE-10 | nested-mutation | evidence | kiss.nested_mutation | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-STATE-11 | aliased-collection-store | on | STATE008 | Retained as an independently selectable rule. |
| HS-STATE-12 | registry-as-global | evidence | state.registry_as_global | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-STATE-13 | global-declaration | on | STATE013 | Retained as an independently selectable rule. |
| HS-STATE-14 | mutable-nonlocal-closure | on | IDIOM007 | Retained as an independently selectable rule. |
| HS-STATE-15 | potential-retention-cycle | evidence | life.potential_retention_cycle | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-STATE-16 | explicit-deletion | hint | NIT004 | Retained as an independently selectable rule. |
| HS-STATE-17 | boolean-state-product | on | STATE014 | Retained as an independently selectable rule. |
| HS-STATE-18 | nullable-state-product | on | STATE015 | Retained as an independently selectable rule. |
| HS-STATE-19 | mutually-dependent-nullability | on | STATE016 | Retained as an independently selectable rule. |
| HS-STATE-20 | none-as-lifecycle-state | evidence | state.none_as_lifecycle_state | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-STATE-21 | duplicated-state-representation | on | STATE017 | Retained as an independently selectable rule. |
| HS-STATE-22 | sentinel-proliferation | evidence | state.sentinel_proliferation | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-STATE-23 | dynamic-attribute-mutation | on | IDIOM009 | Retained as an independently selectable rule. |
| HS-STATE-24 | application-finalizer | on | LIFE010 | Retained as an independently selectable rule. |
| HS-TEST-01 | monkeypatched-global | evidence | coup.monkeypatched_global | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-TEST-02 | env-required-in-test | evidence | coup.env_required_in_test | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-TEST-03 | global-state-reset | evidence | coup.global_state_reset | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-TEST-04 | io-in-unit-test | evidence | coup.io_in_unit_test | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-TEST-05 | call-order-assertion | evidence | coup.call_order_assertion | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-TEST-06 | unconstructible-dependency | evidence | coup.unconstructible_dependency | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-TEST-07 | private-exposed-for-test | evidence | coup.private_exposed_for_test | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
| HS-TEST-08 | no-seam-at-boundary | evidence | coup.no_seam_at_boundary | Retained as hidden evidence and shown only when cited by a finding or `--show-evidence`. |
