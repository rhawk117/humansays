# Humansays Product and System Design

**Status:** Proposed revision grounded in the `pysignals-0.3.0` prototype
**Product:** `humansays`
**Document type:** Product, architecture, quality, and delivery design
**Public release baseline:** `0.1.0` under the new package name
**Supported runtimes:** Python 3.11, 3.12, 3.13, and 3.14
**Initial implementation:** Pure Python using CPython's standard-library AST
**Long-term option:** Optional Rust analysis core behind a stable internal boundary
**Last updated:** 2026-07-25

---

## 1. Executive summary

`humansays` is a deterministic structural review engine for Python code, optimized for code written or modified by coding agents.

The project already has a working prototype under the obsolete name `pysignals`. The prototype is useful evidence and should be iterated upon rather than discarded blindly. It proves that the basic execution model works:

```text
paths or stdin
    -> file discovery
    -> CPython AST parsing
    -> structural fact extraction
    -> signal rules
    -> score and grade
    -> terminal or JSON report
```

However, the prototype is not yet the intended product. It mostly emits isolated signals and threshold findings. The differentiated `humansays` product must correlate multiple signals into evidence-backed review conclusions, explain uncertainty, support coding-agent repair workflows, and prioritize structural regressions over inherited debt.

The target product model is:

```text
source code
    -> parser-neutral structural facts
    -> deterministic raw signals
    -> correlated structural findings
    -> decomposed review scores
    -> exact evidence and repair constraints
```

A raw signal may state that a function spans 78 lines. A `humansays` finding should instead explain that the function likely combines validation, persistence, notification, and environment mutation; show the evidence and source ranges; state what is known versus inferred; and give an agent a bounded review or repair objective.

The prototype is a credible starting point. It is not a specification.

---

## 2. Prototype inspection snapshot

The supplied archive was inspected as a frame of reference.

### 2.1 Observed repository state

| Item | Observed state |
|---|---|
| Archive version | `pysignals-0.3.0` |
| Package name | `pysignals` |
| CLI command | `pysignals` |
| Build backend | Hatchling |
| Package layout | Flat top-level package, not `src/` layout |
| Minimum Python | `>=3.12` |
| Runtime dependencies | Pydantic, pydantic-settings, Rich |
| Package modules | 14 |
| Package source lines | Approximately 2,215 |
| Public signal IDs | `PY001` through `PY022` |
| Test framework | `unittest` |
| Test count observed | 39 |
| Test result observed | 39 passing on Python 3.13.5 |
| GitHub Actions | Not present |
| MkDocs configuration | Not present |
| Release workflow | Not present |
| Lockfile | Not present in the archive |
| License and contribution files | Not present in the archive |

The observed test suite completed successfully in approximately 0.294 seconds in the inspection environment. This is a useful health signal, not a performance benchmark.

### 2.2 Observed self-scan

Running the prototype against its own package produced:

| Metric | Result |
|---|---:|
| Files | 14 |
| Lines | 2,215 |
| Score | 100.0 |
| Grade | A |
| Weighted penalty | 0 |
| Review targets | 20 |
| Remaining signal | `PY011` docstring notices only |
| Parse errors | 0 |

This proves several useful things:

- the package can discover and parse its own source;
- the CLI and JSON renderer work end to end;
- the scanner can enforce some of its own structural policies;
- self-analysis is fast enough to be a practical smoke test;
- the current output model is serializable and deterministic enough for tests.

It also exposes a design flaw: a perfect self-scan still emits 20 review targets because every docstring is treated as a finding. Zero-weight informational observations should not pollute the primary review target count by default.

### 2.3 Status terminology

This document uses four implementation states:

| State | Meaning |
|---|---|
| **Exists** | Implemented and exercised in the prototype |
| **Partial** | Some implementation exists, but it does not satisfy the target product behavior |
| **Missing** | No implementation was found in the prototype |
| **Replace** | The prototype behavior exists but should not remain part of the default product |

---

## 3. What already exists

### 3.1 CLI and input model

**Status: Exists**

The prototype supports:

- files and directories as positional inputs;
- directory traversal for Python files;
- newline-separated file lists through standard input;
- NUL-separated file lists through standard input;
- explicit `-` as a standard-input path source;
- file exclusion by directory or path component;
- symbol filtering;
- terminal and JSON output;
- score-based failure;
- severity-based failure;
- documented nonzero exit codes for findings, missing symbols, and no files.

A deliberate design choice is that version control is not embedded into the scanner. Callers may pipe output from `git`, `rg`, or other tools. This remains a sound composability principle.

What does **not** exist is true diff-aware analysis. Piping changed file names scans only the current file state. It does not compare base and head facts or determine whether a change improved or worsened structure.

### 3.2 Configuration

**Status: Partial**

The prototype supports:

- an explicit TOML file through `--config`;
- automatic discovery of `pysignals.toml`;
- `[tool.pysignals]` in `pyproject.toml`;
- nested threshold, selection, and report sections;
- Pydantic validation;
- command-line overrides;
- environment-variable overrides through a `PYSIGNALS_` prefix.

The public `humansays` product still needs:

- renamed keys, sections, environment prefixes, examples, and error messages;
- `humansays.toml` and optionally `.humansays.toml`;
- a documented and tested discovery root;
- explicit behavior for a nonexistent `--config` path;
- per-rule enable and disable controls;
- rule-specific threshold and severity overrides where justified;
- configuration introspection such as `humansays config show`;
- removal or restriction of hidden environment overrides if reproducibility is preferred;
- path handling relative to the configuration file;
- a stable public configuration schema.

### 3.3 AST parsing and fact extraction

**Status: Exists, but coupled to CPython AST**

The prototype already extracts useful facts:

- aliases and module globals;
- function arguments and boolean parameters;
- validation guards for arguments;
- function span and logical code-line count;
- maximum nesting;
- branch count;
- mutable owners;
- broad exception incidents;
- lazy import incidents;
- standard-library boundary categories;
- instance attribute reads and writes;
- calls to other methods on `self`;
- class attributes;
- class method-to-field cohesion;
- source spans and symbols.

This is the strongest reusable portion of the prototype.

The limitation is that internal models still expose `ast.AST` in several places, including `ParsedModule` and `Scope`. That makes later Rust integration more expensive than necessary. Parser-native nodes should not cross the extraction boundary into the signal and finding layers.

### 3.4 Rule catalog

**Status: Exists**

The prototype has a centralized rule catalog with:

- stable IDs;
- indicator names;
- severity;
- confidence;
- weight;
- review questions.

Centralized metadata is good and should remain.

The current confidence value is fixed per rule, not calculated per finding. A broad exception caught and ignored has the same catalog confidence as a broad exception that immediately re-raises. `humansays` needs evidence-sensitive confidence rather than static confidence alone.

### 3.5 Scoring

**Status: Partial**

The prototype computes:

```text
penalty = sum(weight * confidence)
density = penalty per 100 lines
score = 100 / (1 + density / tolerance)
grade = A through F
```

Advantages:

- deterministic;
- documented;
- normalized by repository size;
- not inflated merely by scanning more clean code;
- easy to test.

Limitations:

- one overall score combines unlike concerns;
- fixed rule confidence directly affects the grade;
- informational signals can distort target counts even when their weight is zero;
- a density score does not distinguish maintainability, review difficulty, change risk, and agent repairability;
- the formula has not been calibrated against human review judgments;
- there is no diff score or structural-regression score.

The existing score can remain temporarily as a compatibility metric, but it should not become the sole product claim.

### 3.6 Reporting

**Status: Partial**

The prototype already provides:

- Rich terminal output;
- stable grouping by file and symbol;
- JSON output;
- a JSON `schema_version`;
- evidence strings;
- review questions;
- deterministic sorting;
- summary counts;
- parse-error collection;
- output truncation.

Missing reporting capabilities include:

- exact location per evidence item;
- known, inferred, and unknown evidence classes;
- repair constraints;
- suggested extraction boundaries;
- verification requirements;
- per-finding score decomposition;
- Markdown;
- SARIF;
- GitHub annotations;
- a formally published JSON Schema;
- schema compatibility tests across releases.

The terminal view currently shows compact indicators but hides most evidence unless JSON is consumed. The human report should provide an optional detailed mode.

### 3.7 Tests

**Status: Exists, but incomplete as a delivery strategy**

The prototype has 39 passing `unittest` tests covering:

- individual AST rules;
- threshold boundaries;
- score behavior;
- TOML overrides;
- command-line precedence;
- stdin input;
- NUL-separated paths;
- exit codes;
- symbol filters;
- fixture consistency;
- JSON serialization;
- self-scan constraints.

This is a respectable prototype test suite.

What is missing:

- pytest-based test organization;
- installed-wheel subprocess tests;
- source-distribution installation tests;
- tests on Python 3.11, 3.12, 3.13, and 3.14;
- Windows and macOS portability checks;
- configuration discovery tests using realistic temporary repositories;
- golden JSON fixtures;
- JSON Schema validation;
- public CLI snapshot tests;
- performance regression tests;
- mutation or property tests for graph algorithms;
- GitHub Actions running any of the above.

---

## 4. Prototype design issues to address

### 4.1 The public model is still signal-first

The prototype's unit of output is an isolated signal. Some rules use multiple facts internally, but the report still presents a flat list such as:

- long function;
- many arguments;
- mixed boundaries;
- several mutation owners.

The intended product should correlate those into a conclusion:

> This function likely combines request validation, persistence, and notification while coordinating several failure-sensitive side effects.

Raw signals remain useful evidence but should not dominate the default report.

### 4.2 Several default rules are ideological rather than contextual

The following prototype rules are too opinionated to remain default high-severity findings:

- any `@staticmethod`;
- any lambda;
- any `from __future__ import annotations`;
- any lazy import;
- every comment;
- every docstring;
- more than one base class without context.

These may remain as:

- supporting signals;
- opt-in rules;
- an opinionated profile;
- evidence contributing to a correlated finding.

They should not define the credibility of the default product.

`from __future__ import annotations` in particular should not be treated as structurally suspicious merely by existing. The rule should be removed unless the project can identify a concrete compatibility or runtime-introspection hazard.

### 4.3 Documentation notices create false review targets

`PY010` and `PY011` have zero scoring weight but still create primary review targets. This makes a perfect score appear noisy and weakens summary metrics.

Target behavior:

- informational observations are disabled by default; or
- they appear in a separate `notices` collection; or
- they are visible only under `--show-signals` or an opt-in profile.

### 4.4 Parse errors do not necessarily fail the scan

The prototype collects parse errors and renders them, but the normal exit policy does not automatically fail when some files cannot be analyzed. A CI run may therefore exit successfully while silently omitting unsupported or malformed files.

Target behavior:

- default local mode may report and continue;
- CI and `--strict` mode must fail on parse or analysis errors;
- JSON must distinguish skipped, failed, and successfully analyzed files;
- summary counts must expose coverage.

### 4.5 Runtime grammar support is implicit

The prototype uses the running interpreter's `ast.parse`. It declares Python `>=3.12`, so it does not currently satisfy the intended Python 3.11–3.14 package support.

The implementation also lacks a target-version policy. A Python 3.11 process cannot parse newer 3.14-only syntax. The documentation and CLI must be honest about this.

MVP policy:

- the package runs on Python 3.11–3.14;
- the CPython backend parses syntax supported by the interpreter running `humansays`;
- `--target-version` may constrain rules but cannot make an older interpreter parse newer grammar;
- CI includes syntax fixtures for each supported runtime;
- future Rust parsing may provide a wider grammar window, but only after parity is proven.

### 4.6 Side-effect classification is narrow

The prototype recognizes selected standard-library modules and mutation methods. It does not understand:

- common database libraries;
- HTTP clients;
- cloud SDKs;
- repository abstractions;
- framework-specific side effects;
- user-defined effect annotations;
- effect ordering;
- transactional relationships.

The existing boundary extraction is a useful seed. It should become a configurable effect registry with confidence levels rather than a hard-coded universal truth.

### 4.7 Parser-native objects leak into shared models

`ParsedModule.tree` and `Scope.node` contain CPython AST objects. If rules, scoring, or reporting come to depend on those models, a Rust backend will require a broad rewrite.

Target rule:

> Parser-native nodes may exist only inside a backend implementation. Shared facts, signals, findings, scores, and reports must contain only stable Python-native scalar and collection types.

### 4.8 Some facts are mutated during analysis

Class cohesion preparation mutates method field-use sets while filtering method names from attribute sets. This makes extracted facts less trustworthy as reusable immutable evidence.

Target behavior:

- extracted facts are immutable after construction;
- transformations create new derived views;
- rule evaluation cannot mutate shared facts;
- golden backend fixtures compare canonical serialized facts.

### 4.9 No cross-file or change graph exists

The prototype analyzes files independently. It cannot currently reason about:

- import cycles;
- dependency magnets;
- call-site impact;
- responsibility movement between modules;
- cross-file shared state;
- structural changes between commits.

These are future capabilities, not hidden prototype features.

### 4.10 Runtime dependency cost is unknown

The prototype depends on Pydantic, pydantic-settings, and Rich. This is acceptable for a prototype, but startup time matters for pre-commit hooks, editor use, and agent loops.

The project should benchmark before rewriting dependencies. Potential future options include:

- retain Pydantic if validation value outweighs startup cost;
- replace pydantic-settings with explicit TOML loading;
- keep Rich as an optional terminal extra;
- use standard-library dataclasses and validation for the core;
- ship a native binary later.

Performance choices must be evidence-driven.

---

## 5. Product thesis

`humansays` becomes better than existing alternatives by optimizing for outcomes they generally do not make central:

1. **Correlated structural findings:** combine several deterministic signal families before making a design-level claim.
2. **Change-aware review:** identify structural regressions rather than merely scanning current state.
3. **Agent-actionable output:** provide exact evidence, constraints, boundaries, and verification steps.
4. **Cosmetic-refactor detection:** identify metric gaming that leaves coupling and responsibility unchanged.
5. **Calibrated restraint:** emit fewer, higher-value findings and measure reviewer agreement.
6. **Deterministic local execution:** require no model call, remote service, or source upload.
7. **Self-auditing operation:** use the tool against its own source as an end-to-end smoke test.
8. **Parser independence:** make a future Rust backend an implementation substitution rather than a product rewrite.

The project should be judged by useful review findings and safe repair outcomes, not by raw rule count.

---

## 6. Competitive position

### 6.1 Existing tool categories

| Category | Typical strength | Gap `humansays` targets |
|---|---|---|
| Formatters and broad linters | Fast local diagnostics and style enforcement | Do not usually correlate structure into review conclusions |
| Type checkers | Type consistency and interface errors | Do not judge responsibility or effect boundaries |
| Complexity tools | Numeric complexity and maintainability metrics | Metrics are not evidence-backed repair guidance |
| Pattern scanners | Declarative syntax and semantic patterns | Structural review requires relationship and change context |
| Hosted AI reviewers | Natural-language feedback | Often nondeterministic, remote, costly, and difficult to gate |
| Code-smell detectors | AST smells and thresholds | Frequently output isolated warnings rather than repair contracts |

### 6.2 Differentiated unit of value

The unit of value is not a rule firing. It is a correlated finding.

```text
Raw facts:
- function span: 78 lines
- code lines: 66
- mutation owners: order, session, cache
- boundary groups: database, filesystem, process
- broad exception handlers: 2
- method field clusters: 3

Raw signals:
- long function
- several mutation owners
- mixed boundaries
- broad exception handling

Correlated finding:
The function likely coordinates several unrelated responsibilities and has an
unclear partial-failure boundary.
```

### 6.3 Claims to avoid

Until measured evidence exists, do not claim that `humansays` is:

- faster than Ruff;
- more comprehensive than Pylint;
- a replacement for type checking or security scanning;
- able to prove runtime effects from syntax;
- an AI reviewer;
- an objective definition of clean code;
- safe to auto-fix every finding.

The defensible claim is:

> `humansays` turns deterministic structural evidence into review findings and bounded repair instructions for coding agents.

---

## 7. Product principles

### 7.1 Deterministic core

The same source, selected backend, configuration, tool version, and runtime target must produce equivalent canonical JSON.

### 7.2 Evidence before judgment

Every inferred finding identifies:

- observed facts;
- derived signals;
- source locations;
- inference rationale;
- uncertainty;
- missing context that could change the conclusion.

### 7.3 Conservative defaults

The default profile optimizes for precision. Low-confidence and ideological checks are opt-in or supporting evidence.

### 7.4 Stable machine interface

Canonical JSON is the public machine interface. Terminal, Markdown, SARIF, and GitHub output are renderers over the same model.

### 7.5 Scores must decompose

A score must explain its factors. The tool must not hide unrelated concerns inside one impressive-looking number.

### 7.6 Configuration must be reproducible

Repository configuration should be visible in source control. Hidden environment overrides are either excluded from v0.1.0 or explicitly reported in `config show`.

### 7.7 The scanner must scan itself

Every CI and release pipeline runs `humansays` against the `humansays` package. This verifies installation, discovery, parsing, configuration, reporting, and exit behavior together.

Self-scan is a smoke test, not proof of correctness. The tool could be changed to forgive its own defects, so golden fixtures and integration tests remain mandatory.

---

## 8. Target domain model

### 8.1 Source spans

```python
@dataclass(frozen=True, slots=True)
class SourceSpan:
    path: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int
```

### 8.2 Structural facts

Facts are parser-neutral observations.

```python
@dataclass(frozen=True, slots=True)
class FunctionFacts:
    symbol: str
    span: SourceSpan
    physical_lines: int
    code_lines: int
    parameters: tuple[str, ...]
    boolean_parameters: tuple[str, ...]
    branch_count: int
    loop_count: int
    handler_count: int
    maximum_nesting: int
    calls: tuple[CallFact, ...]
    mutations: tuple[MutationFact, ...]
    effect_boundaries: tuple[EffectFact, ...]
    field_reads: tuple[str, ...]
    field_writes: tuple[str, ...]
```

No `ast.AST`, Rust node, parser token object, or backend-specific enum may appear here.

### 8.3 Raw signals

```python
@dataclass(frozen=True, slots=True)
class Signal:
    code: str
    subject: SourceSpan
    kind: str
    value: object
    threshold: object | None
    confidence: float
    evidence: tuple[Evidence, ...]
```

Signals are supporting evidence. They may be shown under `--show-signals`.

### 8.4 Correlated findings

```python
@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    title: str
    subject: SourceSpan
    summary: str
    severity: str
    confidence: float
    review_risk: float
    evidence: tuple[Evidence, ...]
    constraints: tuple[str, ...]
    suggested_boundaries: tuple[SuggestedBoundary, ...]
    verification: tuple[str, ...]
```

### 8.5 Evidence classes

Evidence records whether a statement is:

- `observed`;
- `derived`;
- `assumed`;
- `unknown`.

This prevents the tool from presenting a naming heuristic as runtime certainty.

---

## 9. Flagship findings

### 9.1 `HS101`: Mixed responsibilities

Correlates:

- function size;
- disjoint local or field-use clusters;
- effect-boundary groups;
- mutation categories;
- call groups;
- exception regions;
- branch pressure.

It never fires from line count alone.

### 9.2 `HS102`: Side-effect orchestration risk

Correlates:

- multiple observable effects;
- effect ordering;
- exceptions between effects;
- broad handlers;
- partial mutations;
- missing or uncertain compensation.

The language remains cautious when effects are inferred from names or configuration.

### 9.3 `HS201`: Incohesive class

Builds on the existing class field-use graph. It improves the prototype by:

- preserving immutable facts;
- excluding framework and data-model methods through configuration;
- reporting actual method and attribute clusters;
- requiring meaningful separation;
- avoiding a finding from attribute count alone.

### 9.4 `HS202`: Control-flow pressure

Correlates:

- nesting;
- branches;
- loops;
- handlers;
- early exits;
- mutations inside nested paths;
- repeated state checks.

It replaces separate threshold noise with one review conclusion.

### 9.5 Future `HS301`: Structural regression

Compares base and head normalized facts:

- responsibility count;
- effect surface;
- coupling;
- class cohesion;
- control-flow pressure;
- public API impact.

This does not exist in the prototype and is not required for the initial release unless schedule permits.

### 9.6 Future `HS302`: Cosmetic refactor

Detects:

- extracted helpers sharing most state;
- mandatory private helper sequences;
- moved rather than reduced complexity;
- classes introduced only to carry arguments;
- abstraction count rising without boundary reduction.

This is a major future differentiator and requires change-aware facts.

---

## 10. Configuration design

### 10.1 Public files

Version `0.1.0` supports:

- `--config PATH`;
- `humansays.toml`;
- `.humansays.toml`;
- `[tool.humansays]` in `pyproject.toml`.

Only TOML is supported.

### 10.2 Discovery

Recommended discovery:

1. use `--config` exactly when provided;
2. otherwise start from the common root of explicit scan paths, or the current directory for stdin;
3. search that directory for `humansays.toml`, `.humansays.toml`, then `pyproject.toml`;
4. stop after selecting one file;
5. do not merge multiple discovered files in v0.1.0.

A missing explicit path is an error.

### 10.3 Precedence

```text
explicit CLI overrides
    > selected TOML configuration
    > built-in defaults
```

Environment overrides are not required for v0.1.0. If retained from the prototype, they must be:

- renamed to `HUMANSAYS_*`;
- documented;
- shown by `humansays config show --sources`;
- lower priority than explicit CLI options;
- tested against hidden-CI-state surprises.

### 10.4 Initial schema

```toml
[selection]
exclude = ["migrations", "generated", "vendor"]

[analysis]
target_version = "runtime"
strict = true

[report]
format = "terminal"
detail = "findings"
limit = 100
fail_on = "high"
min_score = 0

[rules]
enabled = ["HS101", "HS102", "HS201", "HS202"]
disabled = []

[thresholds.functions]
long_span = 50
dense_lines = 65
max_nesting = 3
max_branches = 5

[thresholds.classes]
minimum_methods_for_cohesion = 4
minimum_fields_for_cohesion = 3

[effects]
database = ["*.save", "*.commit", "*.execute"]
network = ["httpx.*", "requests.*"]
notification = ["*.send", "*.publish", "*.notify"]
```

Pattern semantics must be narrowly defined and tested. Do not ship a vague mini-language.

### 10.5 Rule controls

Every public rule supports:

- enable and disable;
- documented default severity;
- threshold controls only where thresholds are meaningful;
- stable ID;
- `humansays explain HS101`;
- config validation that rejects unknown IDs.

Per-path overrides, inheritance, remote includes, and plugins are deferred.

---

## 11. Target architecture

### 11.1 Proposed package layout

```text
src/humansays/
├── __init__.py
├── __main__.py
├── cli.py
├── application.py
├── config/
│   ├── discovery.py
│   ├── models.py
│   └── loading.py
├── analysis/
│   ├── backend.py
│   ├── models.py
│   ├── cpython_ast.py
│   ├── syntax.py
│   └── effects.py
├── signals/
│   ├── catalog.py
│   ├── functions.py
│   ├── classes.py
│   └── modules.py
├── findings/
│   ├── catalog.py
│   ├── correlate.py
│   └── scoring.py
└── reporting/
    ├── json.py
    ├── terminal.py
    └── models.py
```

A `src/` move is recommended because installed-artifact tests become more meaningful, but it is not worth delaying core finding work if the migration becomes disruptive.

### 11.2 Prototype-to-target mapping

| Prototype module | Target responsibility |
|---|---|
| `core.py` | `application.py` and CLI orchestration |
| `options.py` | `config/` |
| `models.py` | split into config, analysis, finding, and reporting models |
| `syntax.py` | `analysis/syntax.py` |
| `py_ast.py` | `analysis/cpython_ast.py` |
| `rules.py` | split between raw signals and correlated findings |
| `catalog.py` | separate signal and finding registries |
| `scoring.py` | decomposed scoring |
| `report.py` | renderer package |
| `const.py`, `factories.py` | narrow constants and backend helpers |

This is an incremental refactor path, not a rewrite commandment.

### 11.3 Backend protocol

```python
class AnalysisBackend(Protocol):
    name: str
    schema_version: int

    def analyze(
        self,
        files: Sequence[SourceFile],
        options: AnalysisOptions,
    ) -> AnalysisBatch: ...
```

The boundary is batch-oriented so a Rust backend does not cross the Python/native boundary once per AST node.

### 11.4 Backend output

The backend returns normalized facts and backend diagnostics. It does not return:

- CPython AST nodes;
- Rust parser nodes;
- Python wrapper objects for every syntax node.

Rules and findings consume compact facts.

---

## 12. Performance and future Rust integration

### 12.1 Pure Python first

The prototype is already small and fast on itself. The initial work should improve usefulness before introducing native packaging.

Required performance instrumentation:

```text
discovery
reading
parsing
fact extraction
signal evaluation
finding correlation
reporting
total
```

### 12.2 Optimize before porting

Priorities:

1. one main traversal per file;
2. no repeated source tokenization unless required;
3. immutable reusable facts;
4. diff-only input support;
5. early exclusion of generated and vendor files;
6. evaluate only enabled signals;
7. deterministic parallel file analysis only after profiling;
8. content-hash cache after the schema stabilizes.

### 12.3 Rust trigger criteria

Rust work begins only when:

- representative repositories exceed latency targets;
- profiling identifies parsing or extraction as dominant;
- normalized fact schemas are stable;
- backend golden fixtures exist;
- cross-runtime syntax fixtures exist;
- a Rust parser can satisfy Python 3.11–3.14 grammar requirements.

### 12.4 Rust integration constraints

If a Rust backend is added:

- use a batch API;
- return compact normalized facts or final local signals;
- avoid exposing a Rust AST through PyO3;
- maintain canonical output parity;
- use golden fixtures to compare Python and Rust backends;
- preserve the pure-Python backend until parity and wheel coverage are proven;
- consider PyO3 stable ABI targeting Python 3.11+;
- use Maturin or another mature native build backend;
- build wheels for supported OS and architecture combinations;
- retain a documented source-build path.

---

## 13. Testing strategy

### 13.1 Unit tests

Unit tests validate deterministic, isolated behavior.

Required areas:

- source span calculation;
- argument and decorator extraction;
- nesting and branch counts;
- mutation-owner detection;
- effect classification;
- class cohesion components;
- config parsing and validation;
- rule enable and disable behavior;
- signal thresholds;
- correlation formulas;
- confidence computation;
- score decomposition;
- deterministic sorting;
- exit-policy decisions.

Recommended layout:

```text
tests/unit/
├── analysis/
├── config/
├── signals/
├── findings/
├── scoring/
└── reporting/
```

The existing source-string fixtures may be retained and reorganized.

### 13.2 Backend fixture tests

Each syntax feature has a source fixture and canonical normalized fact output.

```text
tests/fixtures/syntax/
├── py311/
├── py312/
├── py313/
└── py314/
```

Golden outputs contain no parser-native object representations.

These tests are the main defense against painful Rust migration.

### 13.3 Correlation tests

Correlation tests prove that:

- one weak signal does not emit a high-level finding;
- independent signal families increase confidence;
- contradictory evidence reduces confidence;
- line length alone never emits mixed responsibility;
- thresholds are inclusive or exclusive exactly as documented;
- the same facts produce the same finding regardless of backend.

### 13.4 Integration tests

Integration tests invoke the CLI through `subprocess`, not by calling `main()` directly.

Required scenarios:

- scan a file;
- scan a directory;
- consume newline-separated stdin;
- consume NUL-separated stdin;
- load explicit `humansays.toml`;
- discover repository configuration;
- load `[tool.humansays]`;
- reject malformed and unknown configuration;
- honor CLI overrides;
- emit parse errors;
- fail in strict mode;
- emit canonical JSON;
- honor symbol filters;
- honor failure thresholds;
- produce expected exit codes.

### 13.5 Installed-artifact tests

CI builds both wheel and source distribution.

For each artifact:

1. create a clean environment;
2. install only the artifact;
3. run `humansays version`;
4. run `humansays --help`;
5. scan a fixture repository;
6. validate JSON;
7. run `humansays` against its own installed source or the checked-out package source.

This catches missing package files and accidental source-tree imports.

### 13.6 Self-scan smoke test

Self-scan is required in three places:

- local test suite;
- normal CI;
- release artifact verification.

Suggested command:

```bash
humansays check src/humansays \
  --config humansays.toml \
  --format json \
  --strict
```

The smoke test asserts:

- exit code matches the repository policy;
- zero parse errors;
- all package files were analyzed;
- JSON validates;
- no forbidden default-profile findings;
- score does not fall below a documented floor;
- output ordering is deterministic.

Do not require a permanent perfect score. As the tool becomes more capable, its own source may expose legitimate review findings. The repository should either fix them or maintain explicit, reviewed baselines with reasons.

### 13.7 Regression and golden tests

Check in focused golden outputs for:

- each public finding;
- combined findings;
- configuration sources;
- output schema;
- self-scan summary shape;
- representative real-world snippets.

Golden files should omit unstable timestamps and absolute paths.

### 13.8 Property tests

Useful targets:

- connected components are order-independent;
- sorting is deterministic;
- adding unrelated clean code does not worsen a density score;
- disabling a rule removes only that rule's contribution;
- serialization round-trips;
- correlation confidence remains in `[0, 1]`.

### 13.9 Benchmark tests

Benchmarks are non-blocking initially.

Corpora:

- the `humansays` repository;
- a medium pure-Python project;
- a large project;
- generated long files;
- many small files;
- syntax fixtures for each supported Python version.

Track:

- cold total time;
- warm total time after caching exists;
- peak memory;
- parse time;
- extraction time;
- correlation time;
- findings per thousand lines;
- reviewer acceptance on labeled fixtures.

---

## 14. GitHub Actions design

### 14.1 `ci.yml`

Triggers:

- pull requests;
- pushes to `main`;
- manual dispatch.

Jobs:

#### Quality

- runner: `vars.DEFAULT_RUNNER || 'ubuntu-24.04'`;
- Python 3.14;
- install locked development environment;
- Ruff format check;
- Ruff lint;
- `ty check`;
- config example validation;
- MkDocs strict build where appropriate.

#### Unit tests

Matrix:

```text
Python 3.11
Python 3.12
Python 3.13
Python 3.14
```

Runs unit, backend fixture, correlation, and library-level tests.

#### Integration tests

Primary Linux matrix across Python 3.11–3.14. Invoke the actual command through subprocess.

#### Portability smoke

- Windows latest with Python 3.14;
- macOS latest with Python 3.14.

Focus on paths, encoding, terminal behavior, subprocess invocation, and installation.

#### Package

- build wheel and source distribution once;
- inspect metadata;
- install each artifact in clean environments;
- run CLI smoke;
- run self-scan;
- upload distributions as artifacts.

#### Required aggregate check

Expose one stable `CI` or `all-green` job for branch protection so matrix renames do not continuously break repository settings.

### 14.2 `docs.yml`

- build MkDocs with `--strict` on documentation-related pull requests;
- generate rule and configuration reference from canonical metadata;
- fail on generated documentation drift;
- deploy GitHub Pages only from `main`;
- use GitHub Pages artifact deployment;
- keep deployment permissions isolated to the deploy job.

### 14.3 `release.yml`

Trigger:

```text
push of v* tag
```

Flow:

1. verify tag matches project version;
2. verify tag commit is reachable from `main`;
3. download or rebuild from the exact tag;
4. run unit and artifact smoke tests or require a reusable verified workflow;
5. self-scan the release artifact;
6. publish to PyPI through Trusted Publishing;
7. create GitHub Release;
8. attach wheel and source distribution;
9. deploy release documentation if versioned docs are later adopted.

The publish job alone receives `id-token: write`. The GitHub release job alone receives `contents: write`.

### 14.4 `benchmarks.yml`

- scheduled weekly and manual;
- does not block pull requests;
- records timing artifacts;
- warns on significant regressions after a stable baseline exists;
- uses pinned benchmark corpora or revisions.

### 14.5 Dependency automation

Dependabot or Renovate should update:

- GitHub Actions;
- Python dependencies;
- future Rust dependencies.

All Actions should eventually be pinned to immutable commit SHAs.

---

## 15. Documentation design

Required documentation:

```text
docs/
├── index.md
├── getting-started/
├── concepts/
│   ├── facts-signals-findings.md
│   ├── confidence.md
│   ├── scoring.md
│   └── limitations.md
├── findings/
├── reference/
│   ├── cli.md
│   ├── configuration.md
│   ├── json-schema.md
│   └── exit-codes.md
├── integrations/
│   ├── github-actions.md
│   ├── pre-commit.md
│   └── coding-agents.md
└── development/
    ├── architecture.md
    ├── adding-a-signal.md
    ├── adding-a-finding.md
    ├── testing.md
    └── rust-backend.md
```

Generate finding pages, rule metadata, configuration keys, and CLI reference where practical. Avoid maintaining the same fact in four files, a traditional documentation technique for producing four different lies.

---

## 16. Delivery roadmap

### Phase 0: Rename and establish the baseline

- rename package, CLI, configuration, schemas, environment variables, and docs;
- decide whether public history starts at `0.1.0`;
- preserve a tagged copy of the prototype;
- run all existing tests before and after rename;
- add a prototype inventory document.

### Phase 1: Quality and packaging foundation

- support Python 3.11–3.14;
- add lockfile;
- add GitHub Actions;
- add wheel and sdist smoke tests;
- add self-scan CI;
- add MkDocs;
- add license, changelog, contribution guidance, and security policy.

### Phase 2: Fact-model stabilization

- remove parser-native objects from shared models;
- make facts immutable;
- add canonical fact serialization;
- add versioned golden fixtures;
- define backend protocol;
- retain CPython backend.

### Phase 3: Correlated MVP findings

- implement `HS101`, `HS102`, `HS201`, and `HS202`;
- demote existing threshold rules to supporting signals;
- remove default docstring and comment targets;
- remove or opt in ideological rules;
- add confidence and evidence decomposition.

### Phase 4: Agent repair contract

- constraints;
- suggested boundaries;
- verification steps;
- repairability;
- stable machine schema.

### Phase 5: Change-aware review

- base/head fact comparison;
- structural regression;
- cosmetic-refactor detection;
- baseline support.

### Phase 6: Performance decision

- benchmark representative projects;
- optimize Python;
- decide whether Rust is justified;
- prototype Rust backend only behind golden parity tests.

---

## 17. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Too many false positives | Conservative defaults, correlation requirements, labeled evaluation corpus |
| Dogmatic style enforcement | Separate profiles; keep ideological signals opt-in |
| Score appears scientific without calibration | Publish decomposition and confidence; label uncalibrated metrics |
| Python static analysis overclaims effects | Distinguish observed, inferred, and unknown |
| Rust migration becomes a rewrite | Parser-neutral facts, batch backend, golden parity fixtures |
| Self-scan becomes circular evidence | Treat it only as smoke; preserve independent fixtures and artifact tests |
| Configuration becomes sprawling | One TOML file, no inheritance or plugins in v0.1.0 |
| Parse errors silently reduce coverage | Strict mode and explicit analyzed/skipped/failed counts |
| Runtime dependencies harm latency | Benchmark startup and staged removal rather than speculative rewrites |
| Rule IDs change after adoption | Stabilize `HS###` IDs before public release |

---

## 18. Prototype rule disposition

| Prototype ID | Prototype behavior | Target disposition |
|---|---|---|
| `PY001` | Many arguments | Supporting signal |
| `PY002` | Boolean mode parameters | Supporting signal or opt-in advisory |
| `PY003` | Deep nesting | Supporting signal for `HS202` |
| `PY004` | Shared mutable state | Retain as a focused finding or strong evidence |
| `PY005` | Broad exception | Retain, but improve context and confidence |
| `PY006` | Multiple mutation owners | Supporting signal for `HS101` and `HS102` |
| `PY007` | Mixed boundaries | Supporting signal for `HS101` and `HS102` |
| `PY008` | Low class cohesion | Promote into `HS201` after fact-model cleanup |
| `PY009` | Long function span | Supporting signal only |
| `PY010` | Every comment | Remove from default findings |
| `PY011` | Every docstring | Remove from default findings |
| `PY012` | Many class attributes | Supporting signal only |
| `PY013` | Attribute prefix cluster | Supporting evidence for hidden components |
| `PY014` | Validated argument bundle | Retain as candidate focused finding |
| `PY015` | Any static method | Move to opinionated profile |
| `PY016` | Any lambda | Move to opinionated profile |
| `PY017` | Long file | Supporting signal or low-severity finding |
| `PY018` | Multiple inheritance | Supporting signal with context |
| `PY019` | Many branches | Supporting signal for `HS202` |
| `PY020` | Future annotations | Remove |
| `PY021` | Lazy import | Opt-in advisory with cycle or dependency context |
| `PY022` | Dense function | Supporting signal for `HS101` and `HS202` |

No compatibility alias is required for `PY###` IDs unless the prototype has external users. The package rename creates a clean opportunity to stabilize the public `HS###` namespace.

---

## 19. Explicitly absent from the prototype

The following capabilities do **not** exist in the inspected archive:

- package or command named `humansays`;
- Python 3.11 support declaration;
- verified Python 3.14 support;
- GitHub Actions;
- GitHub Pages;
- MkDocs;
- PyPI publishing workflow;
- GitHub Release automation;
- wheel and source-distribution smoke tests;
- installed-CLI subprocess integration tests;
- canonical fact schema;
- parser backend abstraction;
- Rust implementation;
- caching;
- parallel analysis;
- cross-file graph;
- built-in diff comparison;
- structural regression findings;
- cosmetic-refactor detection;
- repair constraints;
- suggested extraction spans;
- verification instructions;
- repairability score;
- SARIF;
- GitHub annotations;
- pre-commit configuration;
- rule enable and disable configuration;
- published JSON Schema;
- benchmark workflow;
- adoption or reviewer-acceptance evaluation.

This absence is not a condemnation. It is the implementation backlog.

---

## 20. Success criteria

`humansays` is better than existing alternatives when evidence shows that:

- correlated findings are judged more useful than their raw signals;
- default output remains sparse enough to read;
- reviewers can identify why each finding exists;
- coding agents can consume the JSON without inventing missing context;
- repair attempts preserve stated constraints;
- structural regressions are detected even when one superficial metric improves;
- false-positive rates are measured and reduced;
- the tool scans representative repositories within its latency target;
- the tool can replace its parser backend without changing public findings;
- the project continuously passes unit, integration, artifact, self-scan, documentation, and release checks.

The number of rules is not a success metric.
