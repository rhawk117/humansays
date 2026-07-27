# Python rule book

!!! warning "Superseded"
    This catalog describes the previous rule model and is kept for reference
    only. The current catalog is at [Python rules](../python/index.md).

Every rule cites the section of *Python Code Design and Review Criteria* it
enforces. No rule may exist without a citation. CI reports criteria sections
with zero coverage.

**Read [`README.md`](README.md) before adding or changing a rule.**

## Columns

Each field answers exactly one question. This replaces the earlier two-field
`claim` + `evidence` scheme, which still conflated fact certainty with condition
magnitude — "four arguments is weak evidence, nine is strong" was wrong, because
the count is equally observed in both cases.

| Field | Question | Values |
|---|---|---|
| **Claim** | What kind of assertion? | `bug` incorrect behavior or language hazard · `risk` failure-prone though possibly intentional · `design` maintainability concern |
| **Cert** | Was the condition observed or inferred? | `observed` directly in the fact model · `derived` one inference step · `heuristic` naming or pattern guess |
| **Impact** | How consequential is the likely problem? | **Unassigned until Phase 5.** See below |
| **Report** | May this appear alone? | `standalone` · `evidence` (correlation input only) |
| **Dim** | Evidence dimension, for finding independence | `own` `eff` `cf` `nam` `shp` `cg` `run` |
| **Src** | Where facts come from | `S` static · `C` sharpened by calibration · `O` observed only |

### Why Impact is empty

`impact` exists in the schema and is deliberately unpopulated. Hand-assigning
`high`/`medium`/`low` would be the same unjustified-constant error the critique
log records twice — a new numerology with a nicer name.

Impact is **derived** from the paired before/after corpus in
`.agent-specs/phases/05-measurement-study/PHASE.md`:
a rule whose findings correspond to accepted repairs has demonstrated impact; one
whose findings are routinely left alone has not. No profile may use `impact`
until it is populated from measurement.

Magnitude — four arguments versus nine — affects `impact`, not `Cert`. Until
`impact` exists, magnitude is carried as a numeric field on the finding and
reported, but does not change any classification.

---

## HS-PURPOSE — role and contract (§1, §2)

| ID | Name | Detects | Claim | Cert | Impact | Report | Dim | Src |
|---|---|---|---|---|---|---|---|---|
| `HS-PURPOSE-01` | unclassifiable-role | No dominant role inferable from mutation, effect and return profile | design | heuristic | — | standalone | shp | S/C |
| `HS-PURPOSE-02` | command-query-violation | `get_*`/`is_*`/`has_*`/`find_*` with non-empty field writes | risk | observed | — | standalone | own+nam | S/C |
| `HS-PURPOSE-03` | query-performs-io | Query-named function reaching an effect boundary | design | derived | — | standalone | eff+nam | S/C |
| `HS-PURPOSE-04` | generic-name | `Manager`, `Helper`, `Utils`, `Processor`, `handle`, `process`, `do_*` | design | heuristic | — | standalone | nam | S |
| `HS-PURPOSE-05` | untyped-dict-parameter | `dict[str, Any]`/`dict[str, object]` as operation input | design | observed | — | standalone | shp | S |
| `HS-PURPOSE-06` | untyped-dict-return | Same in return position | design | observed | — | standalone | shp | S |
| `HS-PURPOSE-07` | missing-return-annotation | Public function with no return annotation | design | observed | — | standalone | shp | S |
| `HS-PURPOSE-08` | conjunctive-name | Name contains `and`/`or`, or ≥3 verb stems | design | heuristic | — | standalone | nam | S |
| `HS-PURPOSE-09` | mutation-disguised-as-calculation | Pure-sounding name writing to caller-owned objects | risk | derived | — | standalone | own+nam | S/C |
| `HS-PURPOSE-10` | role-conflict | Decides, performs I/O, and formats output in one body | design | derived | — | standalone | eff+shp | S/C |
| `HS-PURPOSE-11` | undeclared-dependency | Body reaches a name absent from signature and instance state | risk | observed | — | standalone | own | S |

## HS-INPUT — hidden dependencies (§3)

| ID | Name | Detects | Claim | Cert | Impact | Report | Dim | Src |
|---|---|---|---|---|---|---|---|---|
| `HS-INPUT-01` | env-read-in-logic | `os.environ`/`getenv` below module level | risk | observed | — | standalone | eff | S/C |
| `HS-INPUT-02` | clock-read-inline | `datetime.now`, `time.time` in a decision path | risk | derived | — | standalone | eff+cf | S/C |
| `HS-INPUT-03` | randomness-inline | `random.*`, `uuid4`, `secrets.*` in a decision path | risk | derived | — | standalone | eff+cf | S/C |
| `HS-INPUT-04` | module-global-read | Read of a mutable module-level binding | risk | observed | — | standalone | own | S |
| `HS-INPUT-05` | module-global-write | Write to a module-level binding | risk | observed | — | standalone | own | S |
| `HS-INPUT-06` | settings-singleton-access | Import-time-constructed config accessed deep in logic | design | derived | — | standalone | own | S |
| `HS-INPUT-07` | import-time-side-effect | Module body performs I/O, network or filesystem work | risk | observed | — | standalone | eff | S/C |
| `HS-INPUT-08` | constructor-does-work | `__init__` performs I/O or non-trivial computation | design | derived | — | standalone | eff | S/C |
| `HS-INPUT-09` | dependency-count-high | Constructor operation-dependencies > 5 | design | observed | — | standalone | shp | S |

## HS-STATE — ownership and lifetime (§4)

| ID | Name | Detects | Claim | Cert | Impact | Report | Dim | Src |
|---|---|---|---|---|---|---|---|---|
| `HS-STATE-01` | mutable-class-attribute | Class-body `dict`/`list`/`set` literal, incl. `ClassVar[...]` | risk | observed | — | standalone | own | S/O |
| `HS-STATE-02` | mutable-default-argument | `def f(x=[])`, `{}`, `set()` | **bug** | observed | — | standalone | own | S |
| `HS-STATE-03` | leaked-internal-mutable | `return self._x` where `_x` is a mutable collection | risk | observed | — | standalone | own | S/O |
| `HS-STATE-04` | multiple-mutation-owners | Writes to ≥2 distinct owners in one body | design | derived | — | standalone | own | S |
| `HS-STATE-05` | caller-object-mutation | Mutates a parameter the caller owns | risk | observed | — | standalone | own | S/O |
| `HS-STATE-06` | shared-mutable-binding | Module-level mutable bound and mutated from ≥2 scopes | risk | observed | — | standalone | own | S/O |
| `HS-STATE-07` | state-outlives-operation | Field written by one method, read by none | design | derived | — | standalone | own | S |
| `HS-STATE-08` | generic-setter | `set_*` or public attribute write bypassing a transition | design | derived | — | standalone | own+nam | S |
| `HS-STATE-09` | field-write-outside-owner | External code writes another object's non-private attribute | risk | observed | — | standalone | own | S |
| `HS-STATE-10` | nested-mutation | Mutation inside ≥3 levels of nesting | design | observed | — | evidence | own+cf | S |
| `HS-STATE-11` | aliased-collection-store | Stores a parameter collection without copying | risk | derived | — | standalone | own | S/O |
| `HS-STATE-12` | registry-as-global | Module-level dict/list used as a registry | design | derived | — | standalone | own | S/O |

## HS-EFFECT — side effects (§5)

Requires the architecture in `.agent-specs/design/03-effect-architecture.md`.

| ID | Name | Detects | Claim | Cert | Impact | Report | Dim | Src |
|---|---|---|---|---|---|---|---|---|
| `HS-EFFECT-01` | effect-database | Resolves to a database primitive | design | observed | — | evidence | eff | S/C |
| `HS-EFFECT-02` | effect-network | Resolves to a socket or HTTP primitive | design | observed | — | evidence | eff | S/C |
| `HS-EFFECT-03` | effect-filesystem | Resolves to a filesystem primitive | design | observed | — | evidence | eff | S/C |
| `HS-EFFECT-04` | effect-subprocess | Resolves to `subprocess`, `os.system`, `exec*` | design | observed | — | evidence | eff | S/C |
| `HS-EFFECT-05` | effect-notification | Resolves to a broker or notification primitive | design | observed | — | evidence | eff | S/C |
| `HS-EFFECT-06` | mixed-effect-boundaries | ≥2 distinct effect categories in one body | design | derived | — | standalone | eff | S/C |
| `HS-EFFECT-07` | effect-inside-branch | Effect reachable on some paths only | design | derived | — | standalone | eff+cf | S/C |
| `HS-EFFECT-08` | effect-between-mutations | Mutation, then effect, then mutation | risk | observed | — | standalone | eff+own | S/C |
| `HS-EFFECT-09` | unordered-multi-effect | ≥2 effects with no transaction or compensation | risk | derived | — | standalone | eff | S/C |
| `HS-EFFECT-10` | effect-in-domain-type | I/O inside a value object, DTO or entity | design | observed | — | standalone | eff | S/C |
| `HS-EFFECT-11` | effect-in-comprehension | Effect call inside a comprehension or generator | design | observed | — | standalone | eff+cf | S |

## HS-INIT — invariants and construction (§6)

| ID | Name | Detects | Claim | Cert | Impact | Report | Dim | Src |
|---|---|---|---|---|---|---|---|---|
| `HS-INIT-01` | unvalidated-construction | `__init__` assigns parameters with no validation | design | heuristic | — | standalone | shp | S |
| `HS-INIT-02` | post-construction-setup | ≥2 setup-style methods called before first use | design | derived | — | standalone | cg+nam | S/O |
| `HS-INIT-03` | partial-init | Field assigned `None` in `__init__`, set elsewhere | design | observed | — | standalone | own | S |
| `HS-INIT-04` | invariant-bypass | Public attribute duplicating a validated private field | risk | derived | — | standalone | own | S |
| `HS-INIT-05` | missing-transition-method | Status/state field with no domain transitions | design | heuristic | — | standalone | own+nam | S |
| `HS-INIT-06` | exception-leaves-partial-state | Raise between two writes to the same owner | risk | observed | — | standalone | own+cf | S/O |
| `HS-INIT-07` | validated-argument-bundle | Function validates ≥2 of its own arguments internally | design | derived | — | standalone | cf | S |
| `HS-INIT-08` | frozen-candidate | No writes after construction, not frozen | design | observed | — | evidence | own | S/O |
| `HS-INIT-09` | equality-without-invariant | `__eq__` without validated construction | design | observed | — | evidence | shp | S |

## HS-SHAPE — cohesion and control flow (§7, §8, §10, §14)

| ID | Name | Detects | Claim | Cert | Impact | Report | Dim | Src |
|---|---|---|---|---|---|---|---|---|
| `HS-SHAPE-01` | long-function | Span beyond threshold | design | observed | — | standalone | shp | S |
| `HS-SHAPE-02` | dense-function | Code lines beyond threshold | design | observed | — | standalone | shp | S |
| `HS-SHAPE-03` | deep-nesting | Max nesting > 3 (+1 inside a class) | design | observed | — | standalone | cf | S |
| `HS-SHAPE-04` | many-branches | Branch count beyond threshold | design | observed | — | standalone | cf | S |
| `HS-SHAPE-05` | disjoint-local-clusters | Locals form ≥2 non-overlapping use clusters | design | derived | — | standalone | shp | S/O |
| `HS-SHAPE-06` | single-use-private-helper | Private helper with exactly one call site | design | observed | — | evidence | cg | S |
| `HS-SHAPE-07` | helper-chain | ≥3 private helpers callable only in sequence | design | derived | — | standalone | cg | S |
| `HS-SHAPE-08` | narration-extraction | Consecutive one-line helper calls sharing one value | design | derived | — | standalone | cg | S |
| `HS-SHAPE-09` | mixed-abstraction-levels | Raw I/O construction alongside domain decisions | design | derived | — | standalone | eff+shp | S/C |
| `HS-SHAPE-10` | long-module | Module lines beyond threshold | design | observed | — | evidence | shp | S |

## HS-ARGS — arguments (§9)

**Blocked until the argument-kind split lands.** Until `Signature` distinguishes
positional-only, positional-or-keyword, keyword-only, var-positional and
var-keyword with default presence recorded, none of these can be correct. See
`.agent-specs/phases/02-fact-model/PHASE.md`.

| ID | Name | Detects | Claim | Cert | Impact | Report | Dim | Src |
|---|---|---|---|---|---|---|---|---|
| `HS-ARGS-01` | many-operation-arguments | Operation inputs only. 4 weak, 5–6 moderate, 7+ strong | design | observed | — | standalone | shp | S |
| `HS-ARGS-02` | positional-boolean | Boolean parameter that is not keyword-only | design | observed | — | standalone | shp | S |
| `HS-ARGS-03` | boolean-mode-switch | Boolean selecting between two behaviors in the body | design | derived | — | standalone | cf+shp | S/O |
| `HS-ARGS-04` | data-clump | Parameter-name tuple of ≥3 repeated across ≥2 functions | design | derived | — | standalone | shp | S/O |
| `HS-ARGS-05` | dependency-as-argument | Long-lived collaborator passed per call | design | heuristic | — | standalone | shp | S/O |
| `HS-ARGS-06` | optional-not-keyword-only | Defaulted parameter reachable positionally | design | observed | — | standalone | shp | S |
| `HS-ARGS-07` | parameter-bag | Parameter object whose fields are never used together | design | heuristic | — | standalone | shp | S/O |
| `HS-ARGS-08` | untyped-varkwargs | `**kwargs` forwarded without typing or documentation | design | observed | — | evidence | shp | S |
| `HS-ARGS-09` | mutually-exclusive-flags | ≥2 booleans where only one may be true | risk | derived | — | standalone | cf+shp | S/O |

## HS-CLASS — class cohesion (§11)

| ID | Name | Detects | Claim | Cert | Impact | Report | Dim | Src |
|---|---|---|---|---|---|---|---|---|
| `HS-CLASS-01` | low-field-cohesion | Method/field graph splits into ≥2 components | design | derived | — | standalone | own | S |
| `HS-CLASS-02` | many-public-methods | Public methods > 7–10 | design | observed | — | standalone | shp | S |
| `HS-CLASS-03` | many-class-attributes | Attributes beyond threshold | design | observed | — | evidence | shp | S |
| `HS-CLASS-04` | many-private-helpers | Private methods > public methods | design | heuristic | — | standalone | shp | S |
| `HS-CLASS-05` | attribute-prefix-cluster | ≥3 attributes sharing a non-structural prefix | design | derived | — | standalone | nam | S |
| `HS-CLASS-06` | zero-state-namespace | No state, ≤2 stateless methods | design | observed | — | standalone | shp | S |
| `HS-CLASS-07` | stateless-single-method | Class wrapping exactly one stateless method | design | observed | — | standalone | shp | S |
| `HS-CLASS-08` | many-base-classes | ≥2 bases, excluding known mixin/protocol patterns | design | observed | — | evidence | shp | S |
| `HS-CLASS-09` | lsp-signature-drift | Override with incompatible parameters or return | **bug** | derived | — | standalone | shp+cg | S |
| `HS-CLASS-10` | god-constructor | Constructor assigns > 8 fields | design | observed | — | standalone | shp | S |

## HS-FAIL — failure semantics (§12)

| ID | Name | Detects | Claim | Cert | Impact | Report | Dim | Src |
|---|---|---|---|---|---|---|---|---|
| `HS-FAIL-01` | broad-exception-swallowed | `except Exception` with `pass`/`return None` body | risk | observed | — | standalone | cf | S/O |
| `HS-FAIL-02` | broad-exception-logged-only | Caught, logged, execution continues | risk | derived | — | standalone | cf | S/O |
| `HS-FAIL-03` | broad-exception-reraised | Caught and re-raised — counter-evidence | design | observed | — | evidence | cf | S |
| `HS-FAIL-04` | bare-except | `except:` with no type | risk | observed | — | standalone | cf | S |
| `HS-FAIL-05` | absence-collapsed-into-failure | Infrastructure error converted to `None` return | risk | observed | — | standalone | cf+eff | S/O |
| `HS-FAIL-06` | absence-not-modeled | Can return `None` without `\| None` annotation | risk | strong | cf+shp | S |
| `HS-FAIL-07` | exception-as-control-flow | Raise/catch pair inside the same function | design | derived | — | standalone | cf | S/O |
| `HS-FAIL-08` | retry-without-idempotence | Retry loop wrapping a mutating effect | risk | derived | — | standalone | cf+eff | S/C |
| `HS-FAIL-09` | error-message-only | Failure distinguished by message string, not type | design | derived | — | standalone | cf+nam | S |
| `HS-FAIL-10` | finally-suppresses | `return`/`break` inside `finally` | **bug** | observed | — | standalone | cf | S |
| `HS-FAIL-11` | handler-never-fires | Handler with zero executions across the run | design | derived | — | standalone | run | **O** |
| `HS-FAIL-12` | handler-over-broad-observed | Handler caught only one concrete type across N executions | risk | observed | — | standalone | run | **O** |

## HS-TEST — testability (§13)

Requires path-scoped rule activation, which the config schema does not yet
support. See `.agent-specs/phases/02-fact-model/PHASE.md`.

| ID | Name | Detects | Claim | Cert | Impact | Report | Dim | Src |
|---|---|---|---|---|---|---|---|---|
| `HS-TEST-01` | monkeypatched-global | Test patches a module global or attribute | design | observed | — | standalone | own | S |
| `HS-TEST-02` | env-required-in-test | Test reads or sets environment variables | design | observed | — | standalone | eff | S/C |
| `HS-TEST-03` | global-state-reset | Test clears a cache, registry or singleton | risk | observed | — | standalone | own | S/O |
| `HS-TEST-04` | io-in-unit-test | Unit test touches network, database or filesystem | risk | derived | — | standalone | eff | S/C |
| `HS-TEST-05` | call-order-assertion | Test asserts call sequence rather than outcome | design | derived | — | standalone | cg | S |
| `HS-TEST-06` | unconstructible-dependency | Collaborator cannot be built without I/O | design | derived | — | standalone | eff+cg | S/C |
| `HS-TEST-07` | private-exposed-for-test | Attribute made public solely for a test | design | derived | — | standalone | own+cg | S |
| `HS-TEST-08` | no-seam-at-boundary | Effect boundary with no injection point | design | heuristic | — | standalone | eff | S |

## HS-NARRATION — compensating commentary and boilerplate (§7, §8 applied)

**Renamed from `HS-LLM`.** The tool detects narrative structure and compensating
commentary. It cannot infer authorship from that structure, and must not claim
to. Sectioning comments occur legitimately in compiler passes, cryptographic
routines, migration scripts, parsers, numerical procedures, educational
implementations and deliberately linear orchestration code.

Whether generated code has higher incidence is a hypothesis, not a premise. See
`.agent-specs/phases/05-measurement-study/PHASE.md` §4 for
the matched-pair design that tests it. The confounded corpus comparison from the
earlier draft — generated code versus Django — cannot isolate authorship from
framework, age, contributor count, style and domain.

| ID | Name | Detects | Claim | Cert | Impact | Report | Dim | Src |
|---|---|---|---|---|---|---|---|---|
| `HS-NARRATION-01` | sectioning-comment | Comment acting as a step header inside a body | design | derived | — | standalone | nam | S |
| `HS-NARRATION-02` | restating-comment | Comment tokens substantially overlap the statement below | design | heuristic | — | standalone | nam | S |
| `HS-NARRATION-03` | comment-density-high | Comment-to-code ratio above threshold within one function | design | heuristic | — | standalone | nam | S |
| `HS-NARRATION-04` | docstring-restates-signature | Docstring naming only parameters and types | design | derived | — | standalone | nam | S |
| `HS-NARRATION-05` | commented-out-code | Comment that parses as a Python statement | design | observed | — | standalone | nam | S |
| `HS-NARRATION-06` | todo-marker | `TODO`, `FIXME`, `XXX`, `HACK` | design | observed | — | evidence | nam | S |
| `HS-NARRATION-07` | placeholder-implementation | `pass`, `...`, `NotImplementedError` in non-abstract context | risk | observed | — | standalone | shp | S |
| `HS-NARRATION-08` | defensive-redundancy | Type or `None` check guaranteed by annotation and call sites | design | heuristic | — | standalone | cf+cg | S/O |
| `HS-NARRATION-09` | uniform-try-wrapping | Every method wrapped in an identical broad try/except | risk | observed | — | standalone | cf | S |
| `HS-NARRATION-10` | over-parameterized-helper | Helper taking parameters never varied across call sites | design | derived | — | standalone | cg | S/O |
| `HS-NARRATION-11` | symmetric-boilerplate | ≥3 near-identical methods differing only by a literal | design | derived | — | standalone | shp | S |
| `HS-NARRATION-12` | branch-never-taken | Guard evaluated N times, never taken | design | observed | — | standalone | run | **O** |

`HS-NARRATION-02` is the least reliable rule in the catalog. Token overlap is
fuzzy and will misfire on legitimate explanatory comments. It ships at `weak`
and is raised only if measured precision holds on the microfixture corpus.

## HS-LEAK — retention and lifetime (observed only)

No static counterpart. Never contributes to any aggregate.

| ID | Name | Detects | Claim | Cert | Impact | Report | Dim | Src |
|---|---|---|---|---|---|---|---|---|
| `HS-LEAK-01` | instance-growth | Live instances of a project class grow monotonically across repeated operations | risk | observed | — | standalone | run | O |
| `HS-LEAK-02` | project-type-cycle | Reference cycle whose members include project types | design | derived | — | standalone | run | O |
| `HS-LEAK-03` | traceback-retention | Instance holds an object with `__traceback__` | risk | observed | — | standalone | run | O |
| `HS-LEAK-04` | unbounded-container | Module- or class-level collection grows monotonically | risk | observed | — | standalone | run | O |
| `HS-LEAK-05` | finalizer-dependent-release | File or socket closed by GC rather than explicitly | risk | observed | — | standalone | run | O |
| `HS-LEAK-06` | allocation-growth | `tracemalloc` attributes sustained growth to a traceback | design | derived | — | standalone | run | O |
| `HS-LEAK-07` | unbounded-cache | `lru_cache(maxsize=None)` reaching N entries | risk | derived | — | standalone | run | O |

Accuracy note: since PEP 442 (Python 3.4) cycles containing `__del__` **are**
collected. `HS-LEAK-02` is a finalization delay, not a leak — it keeps handles,
sockets and connections open until a collection runs. Report it as a latency and
resource concern. Do not call it a memory leak.

---

## Findings

Findings are separate rules. Each declares the evidence dimensions that must be
independently satisfied. A finding whose supporting signals all trace to one
dimension does not fire.

| ID | Title | `requires_independent` | Claim | Src |
|---|---|---|---|---|
| `HS-FIND-01` | mixed responsibilities | `own` + `eff` + (`shp` or `cf`) | design | S/C |
| `HS-FIND-02` | side-effect orchestration risk | `eff` + `cf` | risk | S/C |
| `HS-FIND-03` | unclassifiable unit | `nam` + `shp` + `eff` | design | S |
| `HS-FIND-04` | missing state owner | `own` + `shp` | design | S |
| `HS-FIND-05` | incohesive class | `own` + `shp` | design | S |
| `HS-FIND-06` | control-flow pressure | `cf` + `shp` | design | S |
| `HS-FIND-07` | ceremonial abstraction | `cg` + `shp` | design | S |
| `HS-FIND-08` | hidden dependency surface | `eff` + `own` | risk | S/C |
| `HS-FIND-09` | untestable without environment | `eff` + `own` + `cg` | risk | S/C |
| `HS-FIND-10` | unprotected invariant | `own` + `cf` | risk | S |
| `HS-FIND-11` | temporal coupling | `cg` + `nam` | design | S/O |
| `HS-FIND-12` | ambiguous failure contract | `cf` + `eff` | risk | S |
| `HS-FIND-13` | silent infrastructure failure | `cf` + `eff` | risk | S/C |
| `HS-FIND-14` | compensating commentary | `nam` + (`shp` or `cf`) | design | S |
| `HS-FIND-15` | dead defensive structure | `run` + `cf` | design | O |

---

## Totals

| Family | Signals |
|---|---:|
| `HS-PURPOSE` | 11 |
| `HS-INPUT` | 9 |
| `HS-STATE` | 12 |
| `HS-EFFECT` | 11 |
| `HS-INIT` | 9 |
| `HS-SHAPE` | 10 |
| `HS-ARGS` | 9 |
| `HS-CLASS` | 10 |
| `HS-FAIL` | 12 |
| `HS-TEST` | 8 |
| `HS-NARRATION` | 12 |
| `HS-LEAK` | 7 |
| **Signals** | **120** |
| **Findings** | **15** |

Claim distribution: **3 `bug`**, 39 `risk`, 78 `design`.

The three `bug` rules today are `HS-STATE-02`, `HS-CLASS-09` and `HS-FAIL-10`.
That count is a **current fact, not a permanent cap.** A future rule detecting a
genuine Python language hazard may legitimately claim `bug`. What the review
process requires is unusual justification for adding one — a cited language
reference or a reproducible incorrect-behavior fixture — not that the number
stays at three forever.

`bug` is deliberately almost empty. Under the earlier tier scheme roughly 32
rules carried the strongest label; three survive the stricter definition. That
collapse is the point — it is what keeps the word meaningful.

## Consequence for the default profile

`default` emits `bug` and `risk` at `moderate` or better, excluding
`HS-NARRATION`. That is approximately 30 rules, not 120 and not the ~32 the
earlier draft implied, and roughly half of them require the effect architecture
before they can fire at all.

**The output guard thresholds in
`.agent-specs/design/02-evaluation-model.md` §5 have
not been re-derived for this claim distribution.** Provisional until measured.

**Profiles are not defined here and must not be inferred from claim types.** An
earlier draft defined `default` as `--claim bug,risk`, which — measured against
this catalog — would have emitted exactly one of the six MVP findings. Profiles
are defined against expected catalog output in
`.agent-specs/design/02-evaluation-model.md` §6 and
enforced by a snapshot test.

**120 is a vocabulary target, not a launch target.** See
`.agent-specs/phases/04-pilot-rules/PHASE.md` for what
actually ships.
