# humansays complete Python rule catalog

**Status:** Proposed canonical design
**Scope:** MVP plus post-MVP Python rules
**Last reconciled:** 2026-07-26

`humansays` is a structural analysis tool that evaluates how difficult Python code will be to understand, test, maintain, and safely modify. It gives humans and coding agents actionable feedback on design problems that traditional linters, type checkers, security scanners, and tests do not detect.

This catalog accounts for every rule in the 22-check prototype, the 120-signal/15-finding expanded catalog, and the 69-signal/5-finding post-MVP plan. A source rule is either retained as a selectable rule, retained as internal evidence, replaced, externalized, or explicitly omitted; nothing is silently discarded.

## 1. Rule model

A rule has independent identity, domain, claim, concern, certainty, emission, and scoring metadata:

- **ID** is a stable domain-prefixed selector such as `STATE001`; severity never appears in the ID.
- **Domain** controls shared analysis configuration and its score contribution.
- **Claim** is `defect`, `risk`, or `design` and describes what the rule asserts.
- **Concern** is `hazard`, `review`, or `advisory` and controls reporting/failure policy independently of domain.
- **Default** is `on`, `hint`, `evidence`, `observe`, or `off`.
- **`weight = 0` reports findings but removes their score contribution; it never disables a rule.**

| Default | Behavior | Score |
|---|---|---:|
| `on` | Emitted by the default profile when its concern is reported | yes |
| `hint` | Emitted by the review profile; intentionally unweighted | no |
| `evidence` | Hidden unless cited by a finding or requested with `--show-evidence` | no |
| `observe` | Requires opt-in runtime observation and never proves absence | no by default |
| `off` | Experimental; enabled only by explicit domain/rule selection | no |

## 2. Domains and default weights

| Domain | Purpose | Weight | Default selection |
|---|---|---:|---|
| `SRP` | Cohesion, responsibility concentration, and reasons to change. | 1.15 | on |
| `KISS` | Accidental complexity, control-flow pressure, and unnecessary indirection. | 1.00 | on |
| `CQS` | Separation of observation, mutation, and commands. | 1.00 | on |
| `POLA` | Behavior that contradicts names, syntax, or ordinary API expectations. | 1.00 | on |
| `COUP` | Dependency visibility, dependency surface, and change coupling. | 1.00 | on |
| `CONTRACT` | Explicit input, output, type, and behavioral contracts. | 0.90 | on |
| `STATE` | State ownership, invariants, transitions, and representable state space. | 1.25 | on |
| `LIFE` | Construction, resource ownership, cleanup, and temporal lifecycle. | 1.15 | on |
| `FAIL` | Failure boundaries, recovery, retries, rollback, and partial effects. | 1.25 | on |
| `CONC` | Task, thread, process, lock, and concurrent-state ownership. | 1.25 | on |
| `IDIOM` | Python-specific semantics whose equivalent rules differ by language. | 0.90 | on |
| `NIT` | Deliberately opinionated reviewer hints; always unweighted by default. | 0.00 | review only |
| `DRY` | Duplicated knowledge and drift risk; experimental and unweighted. | 0.00 | off |

`SOLID`, `CUPID`, `GRASP`, and similar concepts are principle tags or documented selector groups, not ID domains; `YAGNI` is not a static domain because future need cannot be inferred from one source snapshot, and `DRY` stays experimental until it detects duplicated knowledge rather than similar syntax.

## 3. Profiles and selection

```toml
[tool.humansays]
profile = "default"
extend-select = ["NIT", "IDIOM008"]
ignore = ["NIT002"]

[tool.humansays.concerns]
report = ["hazard", "review"]
fail-on = ["hazard"]

[tool.humansays.domains.STATE]
weight = 1.25
min_boolean_dimensions = 3
min_nullable_dimensions = 3
min_state_product = 8

[tool.humansays.domains.NIT]
weight = 0.0

[tool.humansays.per-file-ignores]
"tests/**" = ["DRY"]
"migrations/**" = ["NIT", "DRY"]
```

Selection order is profile → `select` replacement when present → `extend-select` → `ignore` → per-file ignores; ignores always win, and there is no `@` selector syntax.

## 4. Domain thresholds

| Domain | Default knobs |
|---|---|
| `SRP` | `minimum_lines = 40`, `minimum_independent_dimensions = 3`, `max_public_methods = 10`, `max_mutable_attributes = 8` |
| `KISS` | `max_function_lines = 60`, `max_nesting = 4`, `max_branches = 12`, `max_loop_statements = 12`, `max_condition_operands = 3` |
| `COUP` | `max_operation_dependencies = 5`, `data_clump_size = 3`, `data_clump_occurrences = 2` |
| `CONTRACT` | `max_operation_arguments = 5`, `max_positional_record_fields = 2`, `max_dataclass_positional_fields = 3`, `max_generic_parameters = 2` |
| `STATE` | `min_boolean_dimensions = 3`, `min_nullable_dimensions = 3`, `min_state_product = 8`, `max_sentinels = 3` |
| `FAIL` | `max_exception_handlers = 6`, `require_bounded_retry = true` |
| `NIT` | `weight = 0.0`; no rule-specific scoring knobs |
| `DRY` | `weight = 0.0`, `minimum_occurrences = 3`; experimental |

Exact IDs control only selection and suppression; shared knobs live under the domain because per-rule configuration would make the surface impossible to audit.

## 5. Complete selectable rule catalog

Every message template is one sentence and must substitute measured values when available; state-product messages must report the actual representable-state count.

### SRP

Cohesion, responsibility concentration, and reasons to change.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| SRP001 | Role conflict | design | review | on | HS-PURPOSE-10 | Decides, performs I/O, and formats output in one body | `{symbol}` decides policy, performs `{effects}`, and formats output in one body. |
| SRP002 | Effect in domain type | design | review | on | HS-EFFECT-10 | I/O inside a value object, DTO or entity | `{type}` performs `{effect}` even though it is used as a domain value or data carrier. |
| SRP003 | Mixed responsibilities | design | review | on | HS-FIND-01 | own + eff + (shp or cf) | `{symbol}` combines `{responsibilities}` across independent ownership, effect, and control-flow evidence. |
| SRP004 | Mixed abstraction levels | design | review | on | HS-SHAPE-09 | Raw I/O construction alongside domain decisions | `{symbol}` combines domain decisions with low-level `{effect}` construction in the same abstraction layer. |
| SRP005 | Low field cohesion | design | review | on | HS-CLASS-01 | Method/field graph splits into ≥2 components | `{class}` splits into `{component_count}` disconnected method/field components. |
| SRP006 | God constructor | design | review | on | HS-CLASS-10 | Constructor assigns > 8 fields | `{class}.__init__` establishes `{actual}` fields, indicating construction and responsibility pressure. |
| SRP007 | Unclassifiable unit | design | review | on | HS-FIND-03 | nam + shp + eff | `{symbol}` has no dominant role across its name, data flow, effects, and return behavior. |
| SRP008 | Incohesive class | design | review | on | HS-FIND-05 | own + shp | `{class}` contains `{component_count}` independent method/field components with little shared state. |
| SRP009 | Logging mixed with domain mutation | design | review | on | Later combined catalog. | A function mutates domain state and also owns log/report formatting policy. | `{symbol}` mutates `{state}` and builds `{reporting}` output in the same responsibility boundary. |
| SRP010 | Configuration object drives unrelated workflows | design | review | on | Later combined catalog. | A configuration object is read by disjoint method/effect clusters that select separate workflows. | `{type}` supplies `{workflow_count}` unrelated workflow clusters, so configuration has become a responsibility switchboard. |
| SRP011 | Data object used as behavior switchboard | design | review | on | Later combined catalog. | Many branches dispatch behavior from one data object's tag/type fields. | `{symbol}` selects `{branch_count}` behaviors from `{object}.{field}`, making a data carrier own workflow selection indirectly. |

### KISS

Accidental complexity, control-flow pressure, and unnecessary indirection.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| KISS001 | Effect in comprehension | design | review | on | HS-EFFECT-11 | Effect call inside a comprehension or generator | This comprehension performs `{effect}` while presenting the operation as value construction. |
| KISS002 | Helper chain | design | review | on | HS-SHAPE-07 | ≥3 private helpers callable only in sequence | `{class}` contains a chain of `{helper_count}` private helpers that can only execute in one sequence. |
| KISS003 | Boolean mode switch | design | review | on | HS-ARGS-03 | Boolean selecting between two behaviors in the body | Boolean `{parameter}` selects between `{mode_count}` workflows inside `{symbol}`. |
| KISS004 | Control flow pressure | design | review | on | HS-FIND-06 | cf + shp | `{symbol}` combines nesting `{nesting}`, `{branches}` branches, and `{exits}` exits into one control-flow region. |
| KISS005 | Long loop body | design | review | on | HS-SHAPE-13 | Loop body exceeds the configured logical-statement or control-flow threshold | This loop contains 14 statements, four branches and three effects, making iteration and workflow inseparable. |
| KISS006 | Branch pyramid | design | review | on | HS-SHAPE-14 | One operation is buried beneath at least three control-flow layers | The primary operation is reached only after an `if`, loop and nested `if`, indicating guard-clause or extraction pressure. |
| KISS007 | Compound domain condition | design | review | on | HS-SHAPE-15 | Conditional contains more than three Boolean operands or mixes several domain decisions | This predicate has `{operand_count}` Boolean inputs and a theoretical truth table of `{representable_states}` combinations. |
| KISS008 | Repeated type or value dispatch | design | review | on | HS-SHAPE-18 | Conditional chain selects behavior from one type, tag, enum or literal discriminator | Eight branches differ only by the selected callable, so this conditional is functioning as a dispatch dictionary. |
| KISS009 | Exception handler fanout | design | review | on | HS-FAIL-13 | One `try` statement has more than six distinct handlers | This operation defines seven exception branches and five distinct recovery behaviors in one control-flow region. |

### CQS

Separation of observation, mutation, and commands.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| CQS001 | Query mutates owned state | risk | hazard | on | HS-PURPOSE-02 | `get_*`/`is_*`/`has_*`/`find_*` with non-empty field writes | `{symbol}` reads like a query but writes `{fields}`, so callers cannot treat it as observation-only. |
| CQS002 | Query performs I/O | design | review | on | HS-PURPOSE-03 | Query-named function reaching an effect boundary | `{symbol}` reads like a query but reaches `{effects}`, making ordinary-looking observation perform external work. |
| CQS003 | Mutation disguised as calculation | risk | hazard | on | HS-PURPOSE-09 | Pure-sounding name writing to caller-owned objects | `{symbol}` sounds like a calculation but mutates caller-owned `{target}`. |

### POLA

Behavior that contradicts names, syntax, or ordinary API expectations.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| POLA001 | Effectful property | risk | hazard | on | HS-EFFECT-15 | Property performs I/O, mutation, locking, subprocess work or substantial computation | Property `permissions` performs a database query despite being presented as ordinary attribute access. |
| POLA002 | Caller object mutation | risk | hazard | on | HS-STATE-05 | Mutates a parameter the caller owns | `{symbol}` mutates caller-owned `{parameter}` without making destructive behavior explicit. |
| POLA003 | Representation as identity | risk | hazard | on | HS-PURPOSE-15 | `str()` or `repr()` output becomes a persistent key, identifier, filename or protocol value | `repr(entity)` is used as a persistent cache key even though representation output is not an explicit identity contract. |
| POLA004 | Effectful operator overload | risk | hazard | on | HS-EFFECT-16 | Operator method performs I/O, external mutation, subprocess work or notification | `Deployment.__add__` performs network I/O even though `left + right` appears to be a local value operation. |
| POLA005 | None as command | design | review | on | HS-ARGS-12 | `None` selects clearing, resetting, deletion or another alternate operation | Passing `None` to `update_name()` means “clear the name,” hiding a command inside nullability. |
| POLA006 | Non-obvious arithmetic overload | design | review | on | HS-CLASS-17 | Arithmetic, matrix, shift or bitwise operator lacks immediately obvious domain meaning | `{expression}` has no meaning a reader can infer without opening `{method}`; does a reader immediately know what this operation does? |
| POLA007 | Destructive mutation hidden from caller | risk | hazard | on | HS-FIND-19 | own + (nam or shp) | normalize() deletes and rewrites entries in its input mapping although its name and return contract do not communicate destructive mutation. |
| POLA008 | Persistence hidden in helper | risk | hazard | on | Later combined catalog. | A generic helper name reaches a database write or commit boundary. | Helper `{helper}` performs `{persistence_effect}` although its name does not communicate durable mutation. |
| POLA009 | Helper name hides external effects | design | review | on | Later combined catalog. | A generic or pure-looking helper reaches network, filesystem, database, notification, or subprocess effects. | Helper `{helper}` performs `{effects}`, behavior a caller cannot infer from its name. |

### COUP

Dependency visibility, dependency surface, and change coupling.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| COUP001 | Undeclared dependency | risk | hazard | on | HS-PURPOSE-11 | Body reaches a name absent from signature and instance state | `{symbol}` depends on `{dependency}` without receiving it through its signature or owned instance state. |
| COUP002 | Env read in logic | risk | hazard | on | HS-INPUT-01 | `os.environ`/`getenv` below module level | `{symbol}` reads `{variable}` from the environment inside application logic, hiding a replaceable input. |
| COUP003 | Clock read inline | risk | hazard | on | HS-INPUT-02 | `datetime.now`, `time.time` in a decision path | `{symbol}` reads the clock inside a decision path, so identical explicit inputs can produce different decisions. |
| COUP004 | Randomness inline | risk | hazard | on | HS-INPUT-03 | `random.*`, `uuid4`, `secrets.*` in a decision path | `{symbol}` reads randomness inside a decision path without an injection point. |
| COUP005 | Settings singleton access | design | review | on | HS-INPUT-06 | Import-time-constructed config accessed deep in logic | `{symbol}` reaches the process-wide settings singleton `{name}` instead of declaring configuration as a dependency. |
| COUP006 | Hidden dependency surface | risk | hazard | on | HS-FIND-08 | eff + own | `{symbol}` depends on `{dependencies}` through ambient state and effect access rather than its declared contract. |
| COUP007 | Untestable without environment | risk | hazard | on | HS-FIND-09 | eff + own + cg | `{unit}` cannot be constructed or exercised without `{environment}`, according to independent test, ownership, and effect evidence. |
| COUP008 | Single attribute dependency | design | review | on | HS-ARGS-10 | Function accepts an object but only reads one attribute from it | `send_notice()` accepts `User` but depends only on `user.email`, unnecessarily coupling the function to the entire class. |

### CONTRACT

Explicit input, output, type, and behavioral contracts.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| CONTRACT001 | Untyped dict parameter | design | review | on | HS-PURPOSE-05 | `dict[str, Any]`/`dict[str, object]` as operation input | `{symbol}` matches untyped dict parameter: `dict[str, Any]`/`dict[str, object]` as operation input. |
| CONTRACT002 | Untyped dict return | design | review | on | HS-PURPOSE-06 | Same in return position | `{symbol}` matches untyped dict return: Same in return position. |
| CONTRACT003 | Many operation arguments | design | review | on | HS-ARGS-01 | Operation inputs only. 4 weak, 5–6 moderate, 7+ strong | `{symbol}` exposes `{actual}` operation inputs, increasing the contract a caller must understand at once. |
| CONTRACT004 | Optional not keyword only | design | review | on | HS-ARGS-06 | Defaulted parameter reachable positionally | Defaulted parameter `{parameter}` remains positional, allowing call sites to hide which option they change. |
| CONTRACT005 | Mutually exclusive flags | risk | hazard | on | HS-ARGS-09 | ≥2 booleans where only one may be true | `{symbol}` accepts `{flag_count}` flags with `{representable}` combinations although only `{valid}` are valid. |
| CONTRACT006 | Unchecked any operation | risk | hazard | on | HS-PURPOSE-13 | An `Any`-typed value is called, indexed or attribute-accessed | `value` is typed as `Any` but requires `.save()`, so the implementation knows a contract that the annotation omits. |
| CONTRACT007 | Positional record return | design | review | on | HS-PURPOSE-14 | Function returns a tuple with at least three semantically distinct values | `inspect()` returns four positional values whose meanings are unavailable without reading the implementation. |
| CONTRACT008 | Positional dataclass ambiguity | risk | hazard | on | HS-INIT-11 | Dataclass exposes more than three positional fields or adjacent same-typed fields | `Connection` exposes four positional `str` fields that the type checker cannot distinguish when transposed. |
| CONTRACT009 | Type contract friction | design | review | on | HS-FIND-18 | shp + (cg or cf) | value is typed as Any but is repeatedly cast, narrowed and ignored around the same missing contract. |
| CONTRACT010 | Function signature encodes multiple workflows | design | review | on | Later combined catalog. | Disjoint parameter subsets are used on mutually exclusive paths. | `{symbol}` has `{workflow_count}` mutually exclusive parameter subsets, so one signature represents multiple workflows. |

### STATE

State ownership, invariants, transitions, and representable state space.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| STATE001 | Excessive representable state space | risk | hazard | on | HS-FIND-20 | own + cf + shp | `{type}` permits `{representable_states}` structural states although its guards and transitions recognize only `{meaningful_states}` meaningful combinations. |
| STATE002 | Module global read | risk | hazard | on | HS-INPUT-04 | Read of a mutable module-level binding | `{symbol}` reads mutable module binding `{name}`, making its behavior depend on ambient process state. |
| STATE003 | Module global write | risk | hazard | on | HS-INPUT-05 | Write to a module-level binding | `{symbol}` writes module binding `{name}`, giving the function process-wide mutation authority. |
| STATE004 | Mutable class attribute | risk | hazard | on | HS-STATE-01 | Class-body `dict`/`list`/`set` literal, incl. `ClassVar[...]` | `{class}.{field}` is one mutable object shared by every instance of the class. |
| STATE005 | Leaked internal mutable | risk | hazard | on | HS-STATE-03 | `return self._x` where `_x` is a mutable collection | `{symbol}` returns internal mutable `{field}` directly, allowing callers to mutate owned state without the object's contract. |
| STATE006 | Shared mutable binding | risk | hazard | on | HS-STATE-06 | Module-level mutable bound and mutated from ≥2 scopes | Mutable module binding `{name}` is written from `{scope_count}` scopes, leaving no single owner for its transitions. |
| STATE007 | Field write outside owner | risk | hazard | on | HS-STATE-09 | External code writes another object's non-private attribute | `{symbol}` writes `{target}.{field}` from outside the owning object. |
| STATE008 | Aliased collection store | risk | hazard | on | HS-STATE-11 | Stores a parameter collection without copying | `{class}` stores caller-owned collection `{parameter}` directly, so later caller mutation can change internal state. |
| STATE009 | Partial init | design | review | on | HS-INIT-03 | Field assigned `None` in `__init__`, set elsewhere | `{class}.{field}` begins as `None` and is established later, so instances exist in a partially initialized state. |
| STATE010 | Invariant bypass | risk | hazard | on | HS-INIT-04 | Public attribute duplicating a validated private field | `{class}.{public_field}` can bypass validation enforced by `{private_field}`. |
| STATE011 | Missing state owner | design | review | on | HS-FIND-04 | own + shp | `{state}` is mutated from `{owners}` without one explicit lifecycle owner. |
| STATE012 | Unprotected invariant | risk | hazard | on | HS-FIND-10 | own + cf | `{invariant}` can be bypassed through `{paths}`, so valid state is not protected by one construction or transition boundary. |
| STATE013 | Global declaration | risk | hazard | on | HS-STATE-13 | Use of the `global` statement | `global client` gives this function write access to process-wide state with no explicit owner. |
| STATE014 | Boolean state-space explosion | risk | hazard | on | HS-STATE-17 | At least three related Boolean fields represent one lifecycle or responsibility | `{class}` has `{dimension_count}` related Boolean fields, allowing `{representable_states}` possible states although only `{meaningful_states}` appear meaningful. |
| STATE015 | Nullable state-space explosion | risk | hazard | on | HS-STATE-18 | At least three related nullable fields participate in one lifecycle | `{class}` has `{dimension_count}` related nullable fields, allowing `{representable_states}` presence states before lifecycle constraints are applied. |
| STATE016 | Mutually dependent nullability | risk | hazard | on | HS-STATE-19 | Validity of one nullable field depends on another field's presence or absence | `{fields}` permit `{representable_states}` presence combinations although the observed guards accept only `{valid_states}`. |
| STATE017 | Duplicated state representation | risk | hazard | on | HS-STATE-21 | The same state is represented by an enum or status field plus Boolean or nullable fields | `{class}` duplicates lifecycle state across `{fields}`, permitting `{representable_states}` combinations that can disagree. |
| STATE018 | Optional argument state product | risk | hazard | on | HS-ARGS-11 | At least three optional parameters have constrained valid combinations | `{symbol}` permits `{representable_states}` optional-argument combinations although only `{valid_states}` appear valid. |
| STATE019 | State transition without explicit model | risk | hazard | on | Replacement for HS-INIT-05. | The same state field is assigned several domain values from unrelated public methods with repeated guards. | `{class}.{field}` changes through `{transition_count}` ad hoc assignments and repeated guards instead of one explicit transition model. |
| STATE020 | Invariant spread across methods | risk | hazard | on | Later combined catalog. | Related field constraints are checked and repaired in several methods rather than one boundary. | `{invariant}` is enforced across `{method_count}` methods, so no single path establishes or protects valid state. |

### LIFE

Construction, resource ownership, cleanup, and temporal lifecycle.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| LIFE001 | Import time side effect | risk | hazard | on | HS-INPUT-07 | Module body performs I/O, network or filesystem work | Importing `{module}` performs `{effects}`, giving module loading an operational side effect. |
| LIFE002 | Constructor does work | design | review | on | HS-INPUT-08 | `__init__` performs I/O or non-trivial computation | `{class}.__init__` performs `{effects}`, so constructing the object has operational behavior. |
| LIFE003 | Post construction setup | design | review | on | HS-INIT-02 | ≥2 setup-style methods called before first use | `{class}` requires `{setup_count}` setup calls before first use, creating an implicit construction sequence. |
| LIFE004 | Traceback retention | risk | hazard | observe | HS-LEAK-03 | Instance holds an object with `__traceback__` | `{instance}` retains an exception traceback and therefore the frames and locals reachable from it. |
| LIFE005 | Finalizer dependent release | risk | hazard | observe | HS-LEAK-05 | File or socket closed by GC rather than explicitly | Resource `{resource}` was closed by garbage collection rather than an explicit owner. |
| LIFE006 | Unbounded cache | risk | hazard | observe | HS-LEAK-07 | `lru_cache(maxsize=None)` reaching N entries | Unbounded cache `{name}` reached `{entries}` entries during observation. |
| LIFE007 | Temporal coupling | design | review | on | HS-FIND-11 | cg + nam | `{type}` requires the ordered calls `{sequence}` before it becomes usable. |
| LIFE008 | Import time resource construction | risk | hazard | on | HS-INPUT-11 | Module-level construction of clients, connections, pools, executors, threads or processes | `Client()` is constructed during import, giving it process-wide lifetime without an explicit owner. |
| LIFE009 | Import time exit hook | risk | hazard | on | HS-INPUT-17 | `atexit.register()` executed during import | Importing this module registers process-global cleanup behavior through `atexit`. |
| LIFE010 | Application finalizer | risk | hazard | on | HS-STATE-24 | Application class defines `__del__` | `Connection.__del__` hides resource cleanup behind garbage-collection timing instead of an explicit owner. |
| LIFE011 | Overridable call during init | risk | hazard | on | HS-INIT-15 | Constructor calls an overridable instance method | `Base.__init__` calls overridable `configure()` before subclass state is guaranteed to exist. |
| LIFE012 | Callback during construction | risk | hazard | on | HS-INIT-16 | Constructor invokes a caller-provided callback with the object under construction | `Service.__init__` passes `self` to a callback before all fields are initialized. |
| LIFE013 | Self escapes before invariant | risk | hazard | on | HS-INIT-17 | `self` is registered, stored, scheduled or passed externally before construction completes | `self` escapes to `registry.register()` after only four of seven constructor fields are established. |
| LIFE014 | Constructor is an operation | risk | hazard | on | HS-FIND-16 | own + eff + (cf or shp) | Service.__init__ establishes 11 fields, performs two effect categories and contains five branches, so construction has become an operation. |
| LIFE015 | Construction bypasses invariant path | risk | hazard | on | Rewrite of HS-INIT-01. | Alternative construction assigns invariant-bearing fields without using the validated construction path. | `{factory}` constructs `{type}` without the invariant checks used by `{validated_path}`. |
| LIFE016 | Dataclass has a behavior-heavy lifecycle | design | review | on | Later combined catalog. | A dataclass owns several transitions, effects, or lifecycle hooks beyond value behavior. | `{class}` is declared as a dataclass but owns `{transition_count}` transitions and `{effect_count}` effects, so it no longer behaves as a simple data value. |
| LIFE017 | Manual resource management | risk | hazard | on | Later combined catalog. | A resource is acquired and released manually on paths that a context manager could own. | `{symbol}` manually acquires and releases `{resource}` across `{path_count}` paths, leaving cleanup dependent on control flow. |

### FAIL

Failure boundaries, recovery, retries, rollback, and partial effects.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| FAIL001 | Mutation between external effects | risk | hazard | on | HS-EFFECT-08 | Mutation, then effect, then mutation | `{symbol}` mutates state before and after `{effect}`, exposing a partial-state window if the effect fails. |
| FAIL002 | Unordered multi effect | risk | hazard | on | HS-EFFECT-09 | ≥2 effects with no transaction or compensation | `{symbol}` performs `{effect_count}` external effects without an observed transaction, compensation, or idempotent boundary. |
| FAIL003 | Exception leaves partial state | risk | hazard | on | HS-INIT-06 | Raise between two writes to the same owner | `{symbol}` can raise after `{completed_writes}` of `{total_writes}` writes, leaving `{owner}` partially updated. |
| FAIL004 | Broad exception swallowed | risk | hazard | on | HS-FAIL-01 | `except Exception` with `pass`/`return None` body | `{symbol}` catches `{exception}` and continues with `{fallback}`, discarding the original failure. |
| FAIL005 | Absence collapsed into failure | risk | hazard | on | HS-FAIL-05 | Infrastructure error converted to `None` return | `{symbol}` converts `{exception}` into `None`, collapsing infrastructure failure into ordinary absence. |
| FAIL006 | Retry without idempotence | risk | hazard | on | HS-FAIL-08 | Retry loop wrapping a mutating effect | `{symbol}` retries mutating effect `{effect}` without an observed idempotency key, rollback, or compensation policy. |
| FAIL007 | Error message only | design | review | on | HS-FAIL-09 | Failure distinguished by message string, not type | `{symbol}` distinguishes failure behavior by matching message text instead of an explicit exception or result contract. |
| FAIL008 | Side effect orchestration risk | risk | hazard | on | HS-FIND-02 | eff + cf | `{symbol}` coordinates `{effects}` across `{failure_regions}` failure regions without one visible recovery boundary. |
| FAIL009 | Ambiguous failure contract | risk | hazard | on | HS-FIND-12 | cf + eff | `{symbol}` exposes `{failure_modes}` failure modes through the same ambiguous return or exception contract. |
| FAIL010 | Silent infrastructure failure | risk | hazard | on | HS-FIND-13 | cf + eff | `{symbol}` suppresses `{exception}` from `{effect}`, making infrastructure failure indistinguishable from success. |
| FAIL011 | External call inside validation logic | design | review | on | Later combined catalog. | Validation reaches an external effect boundary. | `{validator}` performs `{effect}` while deciding validity, so validation can fail for operational reasons unrelated to the input contract. |
| FAIL012 | Multiple failure modes collapse into one sentinel | risk | hazard | on | Later combined catalog. | Distinct exception or error paths return the same sentinel. | `{symbol}` collapses `{failure_count}` failure modes into `{sentinel}`, forcing callers to guess what happened. |
| FAIL013 | Cleanup can mask the original failure | risk | hazard | on | Later combined catalog. | Cleanup performed during an active exception can raise without preserving the original exception. | `{cleanup}` can raise while handling `{original_exception}`, replacing the failure that triggered cleanup. |
| FAIL014 | Retry has no bounded policy | risk | hazard | on | Later combined catalog. | A retry loop has no attempt, deadline, cancellation, or backoff bound. | `{symbol}` retries `{effect}` without an attempt limit, deadline, or cancellation boundary. |
| FAIL015 | Error handling mutates durable state | risk | hazard | on | Later combined catalog. | An exception handler writes durable state before failure is resolved or re-raised. | The `{exception}` handler writes `{state}` before recovery completes, making error handling part of the durable transition. |

### CONC

Task, thread, process, lock, and concurrent-state ownership.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| CONC001 | Shared state across await | risk | hazard | on | HS-CONC-01 | Shared state is read, an `await` occurs, then state is written from the stale read | `counter` is read before an `await` and written afterward, allowing another task to invalidate the update. |
| CONC002 | Lock held across await | risk | hazard | on | HS-CONC-02 | Async code awaits while holding a lock or semaphore | `{symbol}` matches lock held across await: Async code awaits while holding a lock or semaphore. |
| CONC003 | Blocking call in async | risk | hazard | on | HS-CONC-03 | Async function reaches a known blocking primitive without delegation | `{symbol}` matches blocking call in async: Async function reaches a known blocking primitive without delegation. |
| CONC004 | Concurrency primitive mismatch | risk | hazard | on | HS-CONC-04 | Coordination primitive is used outside the thread, task or process domain it protects | `{symbol}` matches concurrency primitive mismatch: Coordination primitive is used outside the thread, task or process domain it protects. |
| CONC005 | Detached task has no owner | risk | hazard | on | HS-CONC-05 | Created task or submitted work has no retained, awaited or supervised handle | `{symbol}` matches detached task: Created task or submitted work has no retained, awaited or supervised handle. |
| CONC006 | Inconsistent lock order | risk | hazard | on | HS-CONC-06 | Different paths acquire the same locks in different orders | `{symbol}` matches inconsistent lock order: Different paths acquire the same locks in different orders. |
| CONC007 | Race or deadlock observed | defect | hazard | observe | HS-CONC-07 | Instrumentation observes conflicting access, circular waiting or schedule-dependent failure | `{symbol}` matches race or deadlock observed: Instrumentation observes conflicting access, circular waiting or schedule-dependent failure. |
| CONC008 | Async shared scope mutation | risk | hazard | on | HS-CONC-08 | Async function writes a `global` or `nonlocal` binding | `{symbol}` matches async shared scope mutation: Async function writes a `global` or `nonlocal` binding. |
| CONC009 | Async state has no task owner | risk | hazard | on | HS-FIND-17 | own + cf + (cg or run) | Three async functions mutate the same scope binding across suspension points without an identified task-local owner. |
| CONC010 | Async lifecycle is not awaited or closed | risk | hazard | on | Later combined catalog. | An async iterator, context, stream, process, or client is created without an observed await/close/exit owner. | `{resource}` is created in `{symbol}` without an observed await, close, or async-context owner. |
| CONC011 | External await has no timeout boundary | design | review | on | Later combined catalog. | An external await is not dominated by a configured timeout or cancellation scope. | `{symbol}` awaits `{effect}` without an observed timeout or cancellation boundary. |
| CONC012 | Cancellation path can leave partial state | risk | hazard | on | Later combined catalog. | Owned state is mutated across a suspension point without rollback or cancellation-safe ordering. | `{symbol}` mutates `{state}` across an `await`, so cancellation can expose a partially completed transition. |

### IDIOM

Python-specific semantics whose equivalent rules differ by language.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| IDIOM001 | Process hash as identity | risk | hazard | on | HS-PURPOSE-16 | `hash()` output crosses a process boundary or enters persistent storage | `hash(value)` is persisted even though Python hashes may change between processes. |
| IDIOM002 | Context variable created in local scope | risk | hazard | on | HS-CONC-09 | `ContextVar` is created inside a function or closure | `ContextVar("request_id")` is created inside a closure, giving each invocation a new variable retained by its contexts. |
| IDIOM003 | Import path mutation | risk | hazard | on | HS-INPUT-13 | Mutation of `sys.path`, `sys.meta_path`, `sys.path_hooks` or related import machinery | `sys.path.insert()` changes process-global import resolution instead of using the package structure. |
| IDIOM004 | Dynamic namespace access | risk | hazard | on | HS-INPUT-14 | Calls to `locals()` or `globals()` | `locals()` converts implementation-local names into an implicit runtime data contract. |
| IDIOM005 | Module attribute hook | risk | hazard | on | HS-INPUT-15 | Top-level `__getattr__` or `__dir__` | Module-level `__getattr__` makes missing attributes execute dynamic lookup instead of failing normally. |
| IDIOM006 | Module object customization | risk | hazard | on | HS-INPUT-16 | Replacement or class mutation of the current module through `sys.modules` | This module replaces or mutates its own module object, making runtime behavior differ from its source namespace. |
| IDIOM007 | Mutable nonlocal closure | risk | hazard | on | HS-STATE-14 | A nested function writes a `nonlocal` binding | This returned closure mutates `failures` through `nonlocal`, hiding shared state inside lexical scope. |
| IDIOM008 | Numeric truthiness collapses absence | risk | review | hint | Replacement for HS-NARRATION-08; explicit user requirement. | A direct truthiness test is applied to a statically numeric optional value; bool is excluded. | `if not {name}` sends both `0` and `None` through this branch; if zero is valid, compare with `None` explicitly. |
| IDIOM009 | Dynamic attribute mutation | risk | hazard | on | HS-STATE-23 | Dynamic `setattr`, `delattr` or `__dict__.update()` changes object state | `setattr(target, name, value)` mutates an attribute whose existence and type are unavailable to static review. |
| IDIOM010 | Frozen state bypass | risk | hazard | on | HS-INIT-10 | Explicit `object.__setattr__` or `object.__delattr__` | `object.__setattr__` bypasses the frozen object's declared construction and mutation contract. |
| IDIOM011 | Concrete factory return | risk | hazard | on | HS-INIT-13 | Non-final classmethod constructs `cls(...)` but returns the containing class type | `Request.from_bytes()` constructs `cls` but returns `Request`, discarding the subclass-preserving contract of `Self`. |
| IDIOM012 | Stdlib idiom reimplementation | design | review | on | HS-SHAPE-17 | Code matches a curated pattern implemented by the standard library | This `try` and empty `except FileNotFoundError` reimplements `contextlib.suppress`. |
| IDIOM013 | Protocol not runtime-checkable | risk | hazard | on | HS-CLASS-12 | `Protocol` declaration lacks `@runtime_checkable` | Protocol `Repository` declares a program contract but cannot be checked with `isinstance()` at runtime. |
| IDIOM014 | Custom metaclass | risk | hazard | on | HS-CLASS-15 | Application class declares or derives from a custom metaclass | `Service` uses a custom metaclass even though no library-level class-construction requirement is evident. |
| IDIOM015 | Name mangled shadow | risk | hazard | on | HS-CLASS-19 | Base and subclass declare the same source-level mangled name | `Child.__load` does not override `Base.__load` because the two methods are mangled into different names. |
| IDIOM016 | Import inside function or method | design | advisory | hint | Prototype PY021. | An import occurs below module scope outside configured optional-dependency or cycle-breaking boundaries. | `{symbol}` imports `{module}` lazily, hiding an import dependency and possible first-call cost inside execution. |

### NIT

Deliberately opinionated reviewer hints; always unweighted by default.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| NIT001 | Frozen candidate | design | advisory | hint | HS-INIT-08 | No writes after construction, not frozen | `{class}` has no observed post-construction writes, making mutability an unused capability. |
| NIT002 | Zero state namespace | design | advisory | hint | HS-CLASS-06 | No state, ≤2 stateless methods | `{class}` has no state and only `{method_count}` stateless methods, so the class may be a namespace rather than an object. |
| NIT003 | Stateless single method | design | advisory | hint | HS-CLASS-07 | Class wrapping exactly one stateless method | `{class}` wraps one stateless method and adds no state, lifecycle, or polymorphic contract. |
| NIT004 | Explicit deletion | design | review | hint | HS-STATE-16 | Any `del` statement targeting a name, attribute, item or slice | `del {target}` changes state or object shape explicitly; review whether an owned transition or replacement value would make the lifecycle clearer. |
| NIT005 | Exception as control flow | design | advisory | hint | HS-FAIL-07 | Raise/catch pair inside the same function | This exception appears to select an expected branch; review whether an explicit condition would communicate the normal control flow more clearly. |
| NIT006 | Handler over broad observed | risk | advisory | hint | HS-FAIL-12 | Handler caught only one concrete type across N executions | This handler catches `{declared_type}`, while `{execution_count}` observed executions produced only `{observed_types}`; review whether the broader boundary is intentional. |
| NIT007 | Sectioning comment | design | advisory | hint | HS-NARRATION-01 | Comment acting as a step header inside a body | Comment `{comment}` sections a function at a point where responsibility may change; review whether the boundary should be executable. |
| NIT008 | Restating comment | design | advisory | hint | HS-NARRATION-02 | Comment tokens substantially overlap the statement below | Comment `{comment}` substantially repeats the following statement and adds little explanatory context. |
| NIT009 | Comment density high | design | advisory | hint | HS-NARRATION-03 | Comment-to-code ratio above threshold within one function | `{symbol}` has a comment-to-code ratio of `{ratio}`; density is evidence only. |
| NIT010 | Docstring restates signature | design | advisory | hint | HS-NARRATION-04 | Docstring naming only parameters and types | The docstring for `{symbol}` restates parameter names and types without describing behavior or constraints. |
| NIT011 | Todo marker | design | advisory | hint | HS-NARRATION-06 | `TODO`, `FIXME`, `XXX`, `HACK` | `{scope}` contains `{count}` TODO/FIXME/HACK markers; density is project-health evidence only. |
| NIT012 | Placeholder implementation | risk | advisory | hint | HS-NARRATION-07 | `pass`, `...`, `NotImplementedError` in non-abstract context | `{symbol}` contains placeholder implementation `{placeholder}` outside an abstract or stub context. |
| NIT013 | Ceremonial abstraction | design | advisory | hint | HS-FIND-07 | cg + shp | `{abstraction}` adds indirection without observed state, variation, lifecycle, or reused behavior. |
| NIT014 | Compensating commentary | design | advisory | hint | HS-FIND-14 | nam + (shp or cf) | `{symbol}` uses `{comment_count}` comments to mark responsibility changes that also appear in control-flow and shape evidence. |
| NIT015 | Application contract typed as object | design | advisory | hint | HS-PURPOSE-12 | `object` used as an application-level parameter, return, variable, attribute or generic annotation | `value` is annotated as `object`, which communicates no useful application-level type contract. |
| NIT016 | Direct environ index | design | advisory | hint | HS-INPUT-10 | `os.environ[...]` outside tests or the configured configuration boundary | `DATABASE_URL` is read directly inside application logic instead of entering through the configuration boundary. |
| NIT017 | Cached singleton factory | design | advisory | hint | HS-INPUT-18 | Zero-argument cached function returns one process-lifetime object | `{factory}` is a cached zero-argument factory whose mutable result behaves as a process singleton. |
| NIT018 | Missing dataclass slots | design | advisory | hint | HS-INIT-12 | Closed-shape value dataclass does not use `slots=True` | `Coordinate` has a fixed field set but retains a dynamic instance dictionary without an observed use. |
| NIT019 | Nested context managers | design | advisory | hint | HS-SHAPE-16 | A `with` statement directly contains another compatible `with` statement | These context managers can share one `with` statement without changing their lifetime or exception scope. |
| NIT020 | Abc as interface | design | advisory | hint | HS-CLASS-11 | ABC has no state, concrete behavior, construction invariant, registration behavior or lifecycle hooks | `Repository` is an ABC containing only abstract methods, so structural typing could express the contract without inheritance. |
| NIT021 | Name mangled member | design | advisory | hint | HS-CLASS-18 | Class declares a non-dunder member with two leading underscores | `__connect` is name-mangled to `_Service__connect`, preventing ordinary subclass overriding without providing real privacy. |
| NIT022 | Stateless method declared on a class | design | advisory | hint | Prototype PY015; opinionated only. | A static method does not use class identity and has no observed class-specific contract. | `{class}.{method}` uses neither instance nor class state; review whether module scope communicates ownership more clearly. |
| NIT023 | Named behavior expressed as lambda | design | advisory | hint | Prototype PY016; opinionated only. | A non-trivial lambda is assigned, stored, or passed as durable behavior. | This lambda contains `{operation_count}` operations and durable behavior; a named function may communicate its contract more clearly. |
| NIT024 | Inheritance used only for configuration | design | advisory | hint | Later combined catalog. | Subclasses vary only class constants or declarative fields and add no behavior. | `{subclass_count}` subclasses of `{base}` vary configuration values without adding behavior, making inheritance a configuration mechanism. |

### DRY

Duplicated knowledge and drift risk; experimental and unweighted.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| DRY001 | Uniform try wrapping | risk | advisory | off | HS-NARRATION-09 | Every method wrapped in an identical broad try/except | `{class}` wraps `{count}` methods in the same broad exception structure, duplicating one failure policy. |
| DRY002 | Over parameterized helper | design | advisory | off | HS-NARRATION-10 | Helper taking parameters never varied across call sites | Helper `{helper}` accepts `{parameters}` even though every call site supplies the same values. |
| DRY003 | Symmetric boilerplate | design | advisory | off | HS-NARRATION-11 | ≥3 near-identical methods differing only by a literal | `{scope}` contains `{count}` near-identical methods whose only observed variation is `{variation}`. |
| DRY004 | Manual dataclass projection | design | advisory | off | HS-SHAPE-12 | Dataclass is rebuilt as a dictionary with unchanged field names and values | This dictionary manually copies every `User` field and can drift when the dataclass changes. |

## 6. Internal evidence registry

These are real measurements, not independently suppressible public findings; they retain message templates so a correlated finding can cite exact evidence.

| Internal ID | Evidence | Source | Detector/default | Evidence template |
|---|---|---|---|---|
| contract.generic_arity_high | Generic arity high | HS-CLASS-13 | Class declares more than two independent type parameters | `Processor` exposes four independent type dimensions that every caller must understand and supply. |
| contract.positional_boolean | Positional boolean | HS-ARGS-02 | Boolean parameter that is not keyword-only | Boolean parameter `{parameter}` can be passed positionally, hiding its meaning at call sites. |
| contract.template_method_not_final | Template method not final | HS-CLASS-16 | Concrete ABC method orchestrates abstract hooks but lacks `@final` | `run()` defines the invariant order of three abstract hooks but remains overridable by subclasses. |
| contract.validated_argument_bundle | Validated argument bundle | HS-INIT-07 | Function validates ≥2 of its own arguments internally | `{symbol}` repeatedly validates the related arguments `{arguments}`, suggesting a missing input contract. |
| coup.call_order_assertion | Call order assertion | HS-TEST-05 | Test asserts call sequence rather than outcome | Test `{test}` asserts `{call_count}` calls in order, providing evidence of orchestration coupling. |
| coup.data_clump | Data clump | HS-ARGS-04 | Parameter-name tuple of ≥3 repeated across ≥2 functions | Parameters `{parameters}` recur together in `{occurrences}` functions, providing evidence of a shared concept. |
| coup.dependency_count_high | Dependency count high | HS-INPUT-09 | Constructor operation-dependencies > 5 | `{symbol}` matches dependency count high: Constructor operation-dependencies > 5. |
| coup.env_required_in_test | Env required in test | HS-TEST-02 | Test reads or sets environment variables | Test `{test}` must set `{variables}`, providing evidence that configuration is not an explicit dependency. |
| coup.global_state_reset | Global state reset | HS-TEST-03 | Test clears a cache, registry or singleton | Test `{test}` resets `{target}`, providing evidence of process-wide state that outlives one test. |
| coup.implicit_policy_dependency | Implicit policy dependency | HS-INPUT-12 | Related module constants jointly control behavior but are absent from declared dependencies | `fetch()` depends on four module-level retry settings that callers cannot provide or replace. |
| coup.io_in_unit_test | Io in unit test | HS-TEST-04 | Unit test touches network, database or filesystem | Unit test `{test}` reaches `{effect}`, providing evidence that the tested boundary is not isolated. |
| coup.monkeypatched_global | Monkeypatched global | HS-TEST-01 | Test patches a module global or attribute | Test `{test}` monkeypatches `{target}`, providing evidence that production code depends on ambient state. |
| coup.no_seam_at_boundary | No seam at boundary | HS-TEST-08 | Effect boundary with no injection point | Effect boundary `{effect}` has no observed injection, adapter, or replacement seam. |
| coup.parameter_bag | Parameter bag | HS-ARGS-07 | Parameter object whose fields are never used together | `{type}` carries fields used by disjoint operations, suggesting the parameter object combines unrelated inputs. |
| coup.private_exposed_for_test | Private exposed for test | HS-TEST-07 | Attribute made public solely for a test | Tests access `{member}` through a widened API, providing evidence of a missing seam without claiming why the member was exposed. |
| coup.unconstructible_dependency | Unconstructible dependency | HS-TEST-06 | Collaborator cannot be built without I/O | `{dependency}` cannot be constructed without `{effect}`, providing evidence that lifecycle and behavior are coupled. |
| fail.broad_exception_logged_only | Broad exception logged only | HS-FAIL-02 | Caught, logged, execution continues | `{symbol}` catches and logs `{exception}` but continues, so downstream code cannot distinguish success from failure. |
| fail.broad_exception_reraised | Broad exception reraised | HS-FAIL-03 | Caught and re-raised — counter-evidence | `{symbol}` re-raises `{exception}` after handling it, which is counter-evidence against failure suppression. |
| fail.effect_database | Effect database | HS-EFFECT-01 | Resolves to a database primitive | `{symbol}` matches effect database: Resolves to a database primitive. |
| fail.effect_filesystem | Effect filesystem | HS-EFFECT-03 | Resolves to a filesystem primitive | `{symbol}` matches effect filesystem: Resolves to a filesystem primitive. |
| fail.effect_network | Effect network | HS-EFFECT-02 | Resolves to a socket or HTTP primitive | `{symbol}` matches effect network: Resolves to a socket or HTTP primitive. |
| fail.effect_notification | Effect notification | HS-EFFECT-05 | Resolves to a broker or notification primitive | `{symbol}` matches effect notification: Resolves to a broker or notification primitive. |
| fail.effect_subprocess | Effect subprocess | HS-EFFECT-04 | Resolves to `subprocess`, `os.system`, `exec*` | `{symbol}` matches effect subprocess: Resolves to `subprocess`, `os.system`, `exec*`. |
| idiom.accidental_enum_values | Accidental enum values | HS-INIT-14 | Enum uses explicit sequential values with no observed external meaning | `State` assigns sequential integers that create an accidental stable-value contract where `auto()` would express no semantic value. |
| kiss.deep_nesting | Deep nesting | HS-SHAPE-03 | Max nesting > 3 (+1 inside a class) | `{symbol}` reaches nesting depth `{actual}` beyond the configured threshold `{threshold}`. |
| kiss.dense_function | Dense function | HS-SHAPE-02 | Code lines beyond threshold | `{symbol}` contains `{actual}` code lines with little structural separation. |
| kiss.effect_inside_branch | Effect inside branch | HS-EFFECT-07 | Effect reachable on some paths only | `{effect}` occurs only on `{path_count}` control-flow paths, making external behavior path-dependent. |
| kiss.literal_policy_iterable | Literal policy iterable | HS-SHAPE-11 | Loop iterates over inline literals encoding domain states or repeated policy values | This loop embeds four domain states directly in control flow instead of naming the policy they represent. |
| kiss.long_function | Long function | HS-SHAPE-01 | Span beyond threshold | `{symbol}` spans `{actual}` lines; line count is evidence only and must correlate with independent responsibility or control-flow facts. |
| kiss.long_module | Long module | HS-SHAPE-10 | Module lines beyond threshold | Module `{module}` spans `{actual}` lines; size is supporting evidence and not a standalone design conclusion. |
| kiss.many_branches | Many branches | HS-SHAPE-04 | Branch count beyond threshold | `{symbol}` contains `{actual}` branches beyond the configured threshold `{threshold}`. |
| kiss.narration_extraction | Narration extraction | HS-SHAPE-08 | Consecutive one-line helper calls sharing one value | `{symbol}` narrates one workflow as `{call_count}` consecutive one-line helper calls over the same value. |
| kiss.nested_mutation | Nested mutation | HS-STATE-10 | Mutation inside ≥3 levels of nesting | `{symbol}` mutates `{target}` at nesting depth `{depth}`, making the transition conditional and difficult to locate. |
| kiss.single_use_private_helper | Single use private helper | HS-SHAPE-06 | Private helper with exactly one call site | Private helper `{helper}` has one call site and supplies extraction evidence without proving the boundary is unnecessary. |
| life.allocation_growth | Observed allocation retention growth | HS-LEAK-06 | `tracemalloc` attributes sustained growth to a traceback | `tracemalloc` attributes `{growth}` sustained bytes to `{traceback}`; this is retention evidence, not proof of a leak. |
| life.instance_growth | Observed instance retention growth | HS-LEAK-01 | Live instances of a project class grow monotonically across repeated operations | Live instances of `{type}` increased from `{start}` to `{end}` across `{operations}` repeated operations; this is retention evidence, not proof of a leak. |
| life.potential_retention_cycle | Potential retention cycle | HS-STATE-15 | Static ownership path forms a cycle through callbacks, bound methods, tasks or parent-child references | `Service` registers its own bound method in a longer-lived registry, creating a potential retention cycle. |
| life.project_type_cycle | Observed project-type reference cycle | HS-LEAK-02 | Reference cycle whose members include project types | Observed objects of `{types}` form a reference cycle; review finalization latency and retained resources rather than assuming a leak. |
| life.unbounded_container | Observed shared-container growth | HS-LEAK-04 | Module- or class-level collection grows monotonically | Shared container `{name}` grew from `{start}` to `{end}` across `{operations}` operations without observed release. |
| life.unvalidated_construction | Unvalidated construction | HS-INIT-01 | `__init__` assigns parameters with no validation | `{class}` appears to have invariant-sensitive fields, but construction assigns them directly while validation and transition checks occur elsewhere. |
| srp.attribute_prefix_cluster | Attribute prefix cluster | HS-CLASS-05 | ≥3 attributes sharing a non-structural prefix | `{class}` has `{count}` attributes in prefix cluster `{prefix}`, suggesting an internal responsibility boundary. |
| srp.conjunctive_name | Conjunctive name | HS-PURPOSE-08 | Name contains `and`/`or`, or ≥3 verb stems | `{symbol}` matches conjunctive name: Name contains `and`/`or`, or ≥3 verb stems. |
| srp.disjoint_local_clusters | Disjoint local clusters | HS-SHAPE-05 | Locals form ≥2 non-overlapping use clusters | `{symbol}` contains `{cluster_count}` disjoint local-variable clusters, suggesting independent responsibilities. |
| srp.generic_name | Generic name | HS-PURPOSE-04 | `Manager`, `Helper`, `Utils`, `Processor`, `handle`, `process`, `do_*` | `{symbol}` matches generic name: `Manager`, `Helper`, `Utils`, `Processor`, `handle`, `process`, `do_*`. |
| srp.many_base_classes | Many base classes | HS-CLASS-08 | ≥2 bases, excluding known mixin/protocol patterns | `{class}` has `{actual}` base classes; count is evidence only after mixins and protocols are excluded. |
| srp.many_class_attributes | Many class attributes | HS-CLASS-03 | Attributes beyond threshold | `{class}` owns `{actual}` attributes; count is evidence that must correlate with lifecycle or cohesion facts. |
| srp.many_private_helpers | Many private helpers | HS-CLASS-04 | Private methods > public methods | `{class}` has `{actual}` private helpers; this may be good decomposition unless method and field clusters also diverge. |
| srp.many_public_methods | Many public methods | HS-CLASS-02 | Public methods > 7–10 | `{class}` exposes `{actual}` public methods; count is evidence that must correlate with cohesion or responsibility facts. |
| srp.mixed_effect_boundaries | Mixed effect boundaries | HS-EFFECT-06 | ≥2 distinct effect categories in one body | `{symbol}` crosses `{effect_count}` effect categories (`{effects}`), increasing coordination and failure-boundary pressure. |
| srp.private_method_count_high | Private method count high | HS-CLASS-14 | Class declares more than six private methods | `BuildCoordinator` has 11 private methods split across Git, subprocess and reporting responsibilities. |
| srp.unclassifiable_role | Unclassifiable role | HS-PURPOSE-01 | No dominant role inferable from mutation, effect and return profile | `{symbol}` matches unclassifiable role: No dominant role inferable from mutation, effect and return profile. |
| state.generic_setter | Generic setter | HS-STATE-08 | `set_*` or public attribute write bypassing a transition | `{symbol}` exposes a generic setter for `{field}` instead of naming the state transition it performs. |
| state.multiple_mutation_owners | Multiple mutation owners | HS-STATE-04 | Writes to ≥2 distinct owners in one body | `{symbol}` writes state owned by `{owners}`, so one operation spans multiple mutation authorities. |
| state.none_as_lifecycle_state | None as lifecycle state | HS-STATE-20 | `None` represents pending, failed, closed, unavailable or another domain state | `None` represents the pending state for `result`, hiding lifecycle meaning inside nullability. |
| state.registry_as_global | Registry as global | HS-STATE-12 | Module-level dict/list used as a registry | Module collection `{name}` behaves as a process-wide registry without an explicit lifecycle owner. |
| state.sentinel_proliferation | Sentinel proliferation | HS-STATE-22 | Module or class defines several identity sentinels for implicit modes | This module defines four distinct sentinels, indicating an API with several implicit absence modes. |
| state.state_outlives_operation | Write-only attribute | HS-STATE-07 | Field written by one method, read by none | `{class}.{field}` is written by `{writer}` but never read by the class, suggesting retained state without an owned purpose. |

## 7. Explicit externalizations, replacements, and omissions

Externalized checks may remain as raw facts when they strengthen a humansays finding, but humansays does not emit their standalone diagnostic.

| Source rule | Original name | Decision | Replacement | Explicit reason |
|---|---|---|---|---|
| HS-ARGS-05 | dependency-as-argument | omitted | — | Passing a dependency explicitly is normally healthier than hiding it in ambient state, so the original rule would push design in the wrong direction. |
| HS-ARGS-08 | untyped-varkwargs | external | — | Untyped `**kwargs` is directly covered by Ruff ANN003 and type checkers without a meaningful structural extension. |
| HS-CLASS-09 | lsp-signature-drift | external | — | Override signature compatibility is already checked precisely by type checkers, while behavioral substitutability cannot be established from signatures alone. |
| HS-EFFECT-12 | dynamic-python-execution | external | — | Standalone `eval`/`exec` detection is already owned by Bandit/Ruff security rules; humansays may retain the effect fact for higher-order findings. |
| HS-EFFECT-13 | process-image-replacement | external | — | Standalone `os.exec*` detection is security and process-policy linting; humansays only needs it as an effect and lifecycle fact. |
| HS-EFFECT-14 | shell-command-execution | external | — | Shell execution and `shell=True` are already covered by Bandit's shell-injection checks, leaving no unique standalone humansays claim. |
| HS-FAIL-04 | bare-except | external | — | Bare `except` is a conventional lint diagnostic already owned by Ruff/Pylint. |
| HS-FAIL-06 | absence-not-modeled | external | — | A return annotation that omits `None` is type-checker territory; humansays only retains correlated evidence when distinct failure paths collapse into absence. |
| HS-FAIL-10 | finally-suppresses | external | — | Control flow in `finally` is already reported by Ruff B012 with no structural inference needed. |
| HS-FAIL-11 | handler-never-fires | omitted | — | A handler not firing during one observation window does not establish that it is unreachable or unnecessary. |
| HS-FIND-15 | dead defensive structure | omitted | — | Runtime non-execution cannot justify the finding's claim that defensive structure is dead. |
| HS-INIT-05 | missing-transition-method | replaced | STATE transition-without-explicit-model | The absence of a named transition method proves nothing, so it is replaced by a rule that requires repeated ad hoc state writes and transition guards. |
| HS-INIT-09 | equality-without-invariant | omitted | — | Defining equality does not imply that construction validation or a stronger invariant is required. |
| HS-NARRATION-05 | commented-out-code | external | — | Commented-out code is directly covered by Ruff ERA001/eradicate-style checks and does not require correlated structural analysis. |
| HS-NARRATION-08 | defensive-redundancy | replaced | IDIOM008 | The broad defensive-redundancy claim trusted annotations and observed call sites too much; it is replaced by the narrow numeric truthiness rule IDIOM008. |
| HS-NARRATION-12 | branch-never-taken | omitted | — | An untaken branch in one runtime sample is coverage evidence, not proof that the branch is dead. |
| HS-PURPOSE-07 | missing-return-annotation | external | — | Missing return annotations are owned by annotation linters and type checkers; humansays gains no structural inference by repeating the standalone diagnostic. |
| HS-STATE-02 | mutable-default-argument | external | — | Mutable argument defaults are a mature correctness check in Ruff B006 and need no higher-order humansays rule unless used as evidence of shared-state ownership. |

Official overlap references used for these decisions: [Ruff rule index](https://docs.astral.sh/ruff/rules/), [Ruff ANN003](https://docs.astral.sh/ruff/rules/missing-type-kwargs/), [Bandit shell-injection checks](https://bandit.readthedocs.io/en/latest/plugins/index.html), and [mypy override checks](https://mypy.readthedocs.io/en/stable/error_code_list.html#check-validity-of-overrides-override).

## 8. Prototype `PY001`–`PY022` crosswalk

| Prototype ID | Prototype check | Final disposition |
|---|---|---|
| `PY001` | many arguments | HS-ARGS-01 |
| `PY002` | boolean modes | HS-ARGS-03 |
| `PY003` | deep nesting | HS-SHAPE-03 |
| `PY004` | shared mutable state | HS-STATE-06 |
| `PY005` | broad exception | HS-FAIL-01/02/03 |
| `PY006` | mutation owners | HS-STATE-04 |
| `PY007` | mixed boundaries | HS-EFFECT-06 and HS-FIND-01/02 |
| `PY008` | low class cohesion | HS-CLASS-01 and HS-FIND-05 |
| `PY009` | long function | HS-SHAPE-01 |
| `PY010` | comments | omitted: raw comment count was noisy and duplicated narration evidence |
| `PY011` | docstrings | omitted: raw docstring count did not establish a structural problem |
| `PY012` | many class attributes | HS-CLASS-03 |
| `PY013` | attribute prefix clusters | HS-CLASS-05 |
| `PY014` | validated argument bundle | HS-INIT-07 |
| `PY015` | static method | NIT rule; reviewer hint only |
| `PY016` | lambda | NIT rule; reviewer hint only |
| `PY017` | long file | HS-SHAPE-10 |
| `PY018` | many base classes | HS-CLASS-08 |
| `PY019` | many branches | HS-SHAPE-04 |
| `PY020` | future annotations | omitted: version-dependent modernization belongs to Ruff and loses value on newer Python |
| `PY021` | lazy import | IDIOM rule; reviewer hint only |
| `PY022` | dense function | HS-SHAPE-02 |

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

## 10. Accounting summary

- Existing catalog: **120 signals + 15 findings**.
- Post-MVP plan: **69 signals + 5 findings**.
- Final selectable catalog, including later combined rules: **158 rules**.
- Internal evidence facts: **57**.
- Explicit externalized/replaced/omitted source entries: **18**.
- Prototype crosswalk: **22 of 22** checks accounted for.
- Source-catalog crosswalk: **209 of 209** entries accounted for.

The default profile remains advisory unless the user configures `fail-on`; `NIT` and `DRY` remain reportable but unweighted, runtime observations never prove absence, and weak measurements never become structural conclusions without independent evidence.
