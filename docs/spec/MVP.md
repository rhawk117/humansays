# Humansays v0.1.0 MVP Specification

**Status:** Proposed implementation plan grounded in the `pysignals-0.3.0` prototype
**Release:** `0.1.0`
**Package and command:** `humansays`
**Supported runtimes:** Python 3.11, 3.12, 3.13, and 3.14
**Implementation:** Pure Python with the CPython AST backend
**Prototype relationship:** Rename and evolve the prototype; do not claim the target design already exists
**Last updated:** 2026-07-25

---

## 1. Purpose

Version `0.1.0` is the first public release under the `humansays` name.

The supplied `pysignals-0.3.0` archive is a working prototype, not an empty scaffold. It already provides a CLI, TOML configuration, 22 AST-derived signals, scoring, terminal and JSON reports, and 39 passing tests. The MVP should preserve useful behavior while correcting the most important product and architecture problems.

The release must prove this claim:

> `humansays` can turn several deterministic Python structure signals into a small number of evidence-backed review findings, emit stable machine-readable output, and run reliably in local, CI, and coding-agent workflows.

The MVP must not present prototype-only capabilities as completed product features.

---

## 2. Prototype baseline

### 2.1 What exists and should be reused

- file and directory discovery;
- newline and NUL-separated stdin input;
- CPython AST parsing;
- source spans and symbol locations;
- argument and boolean-parameter extraction;
- branch and nesting extraction;
- mutation-owner collection;
- standard-library boundary classification;
- broad exception detection;
- class field-use cohesion analysis;
- centralized rule metadata;
- density-based score and grade;
- terminal and JSON output;
- JSON schema version field;
- TOML and `pyproject.toml` configuration;
- command-line overrides;
- symbol filtering;
- exit-code logic;
- source-string fixtures;
- a self-scan test.

### 2.2 What exists but must change

| Prototype behavior | MVP change |
|---|---|
| Package and CLI named `pysignals` | Rename to `humansays` |
| `PY###` public IDs | Introduce stable `HS###` finding IDs |
| Python `>=3.12` | Support and test 3.11–3.14 |
| Flat isolated signals | Preserve as internal evidence and add correlated findings |
| Fixed confidence per rule | Compute confidence from evidence where possible |
| Every comment and docstring is a target | Disable or separate from default findings |
| Any static method or lambda is a warning | Move to opt-in opinionated signals |
| Future annotations is a warning | Remove |
| Parse errors may still allow success | Strict CI mode fails on incomplete analysis |
| `unittest` only | Migrate or supplement with pytest organization |
| In-process CLI tests | Add installed-command subprocess tests |
| Parser objects in shared models | Introduce parser-neutral fact boundary |
| Environment prefix `PYSIGNALS_` | Rename or remove from v0.1.0 |
| `pysignals.toml` | Replace with `humansays.toml` |
| No Actions or release automation | Add CI, docs, package, and release workflows |

### 2.3 What does not exist

The following are new work:

- correlated findings;
- repair constraints;
- exact evidence classification;
- GitHub Actions;
- MkDocs and Pages;
- wheel and source-distribution smoke tests;
- verified Windows and macOS execution;
- published JSON Schema;
- backend protocol;
- backend golden fixtures;
- diff comparison;
- caching;
- Rust core.

Only the first group required by the MVP is included below.

---

## 3. Release strategy

The prototype is versioned `0.3.0`, but the package name changes. `humansays` may begin at `0.1.0` without pretending that package versions are globally sacred runes.

Required repository history:

1. retain or tag the prototype snapshot;
2. rename the project in one focused change;
3. keep all prototype tests passing during the rename;
4. add new behavior incrementally;
5. record which prototype rules were retained, demoted, replaced, or removed.

The MVP is not a ground-up rewrite.

---

## 4. User outcome

A user can install and run:

```bash
uvx humansays check src/
```

or, if the CLI remains commandless for the initial migration:

```bash
uvx humansays src/
```

The preferred public shape is subcommand-based:

```bash
humansays check [PATH ...]
humansays explain HS101
humansays config show
humansays config validate
humansays version
```

Example report:

```text
Humansays: C+

src/orders/service.py:42-119 HS101 mixed-responsibilities [high]
  This function appears to combine validation, persistence, and notification.

  Observed:
    - 78 source lines
    - 3 effect-boundary groups
    - 3 mutation owners
    - 2 broad exception regions

  Inferred:
    - at least 3 responsibility clusters

  Confidence: 0.84
  Review risk: 7.2/10

1 finding across 14 files
```

The default terminal report emphasizes findings, not every supporting signal.

---

## 5. MVP scope

### 5.1 Included

- rename package and CLI to `humansays`;
- Python 3.11–3.14 runtime support;
- retained file, directory, and stdin input modes;
- custom TOML configuration;
- `[tool.humansays]` support;
- explicit `--config PATH`;
- CPython AST backend;
- parser-neutral normalized facts for data consumed by public rules;
- four correlated findings;
- optional display of retained raw signals;
- terminal and canonical JSON output;
- deterministic ordering;
- strict analysis mode;
- score and grade, with documented provisional status;
- unit tests;
- subprocess integration tests;
- wheel and sdist installation tests;
- self-scan smoke tests;
- GitHub Actions;
- MkDocs strict build;
- GitHub Pages deployment;
- PyPI Trusted Publishing;
- GitHub Release creation;
- architecture seams for later Rust integration.

### 5.2 Excluded

- Rust or native extensions;
- full cross-file call resolution;
- built-in Git base/head comparison;
- cosmetic-refactor detection;
- automatic code changes;
- LLM calls;
- plugins;
- caching;
- parallel processing;
- SARIF;
- GitHub review comments;
- LSP;
- configuration inheritance;
- remote configuration;
- support below Python 3.11;
- support for non-Python languages.

Diff-aware review and cosmetic-refactor detection remain high-priority follow-up work.

---

## 6. Public findings

The MVP exposes four correlated findings. Existing `PY###` prototype checks become internal signals or opt-in diagnostics.

### 6.1 `HS101`: Mixed responsibilities

**Purpose:** Identify a function with evidence of several independent reasons to change.

Must require at least three independent signal families. Line count alone is insufficient.

Candidate evidence:

- physical and logical line count;
- effect-boundary groups;
- mutation-owner count;
- call-name or variable-use clusters;
- exception regions;
- branch pressure;
- unrelated validation groups.

Minimum initial policy:

```text
emit when:
  at least 3 independent signal families contribute
  and at least 1 of:
    effect groups >= 2
    mutation owners >= 2
    responsibility clusters >= 2
```

Confidence increases when independent evidence agrees.

### 6.2 `HS102`: Side-effect orchestration risk

**Purpose:** Identify a function coordinating several observable mutations or external effects with unclear failure handling.

Evidence:

- several mutation owners;
- multiple effect categories;
- broad exceptions;
- effects inside nested branches;
- effects before and after potentially failing operations;
- unknown effect semantics inferred from configured names.

The report must state which effect classifications are observed and which are inferred.

### 6.3 `HS201`: Incohesive class

**Purpose:** Identify classes whose meaningful methods operate on mostly disconnected instance state.

This evolves the existing prototype cohesion algorithm.

Requirements:

- facts remain immutable;
- method-name filtering does not mutate the source facts;
- trivial accessors and selected lifecycle methods are excluded;
- output lists method and field clusters;
- class size alone cannot trigger the finding;
- minimum method and field counts are configurable.

### 6.4 `HS202`: Control-flow pressure

**Purpose:** Identify functions that combine several review-hostile control-flow properties.

Evidence:

- branch count;
- maximum nesting;
- loops;
- exception handlers;
- early exits;
- mutations in nested control paths;
- repeated state checks.

A function with one high metric and otherwise simple structure should normally produce a raw signal, not this finding.

---

## 7. Prototype signal disposition in v0.1.0

| Old ID | Old indicator | MVP use |
|---|---|---|
| `PY001` | many arguments | Internal signal |
| `PY002` | boolean modes | Internal or opt-in signal |
| `PY003` | deep nesting | `HS202` evidence |
| `PY004` | shared mutable state | Retain as focused diagnostic or `HS102` evidence |
| `PY005` | broad exception | Retain and use as `HS102` evidence |
| `PY006` | mutation owners | `HS101` and `HS102` evidence |
| `PY007` | mixed boundaries | `HS101` and `HS102` evidence |
| `PY008` | low class cohesion | Basis for `HS201` |
| `PY009` | long function | Internal signal |
| `PY010` | comments | Disabled by default |
| `PY011` | docstrings | Disabled by default |
| `PY012` | many class attributes | `HS201` evidence |
| `PY013` | prefix clusters | `HS201` evidence |
| `PY014` | validated argument bundle | Optional focused diagnostic |
| `PY015` | static method | Opinionated profile only |
| `PY016` | lambda | Opinionated profile only |
| `PY017` | long file | Low-severity or internal signal |
| `PY018` | many base classes | Internal signal |
| `PY019` | many branches | `HS202` evidence |
| `PY020` | future annotations | Removed |
| `PY021` | lazy import | Opt-in advisory |
| `PY022` | dense function | `HS101` and `HS202` evidence |

Do not preserve public compatibility aliases unless external use of the prototype is confirmed.

---

## 8. CLI contract

### 8.1 Commands

```bash
humansays check [PATH ...]
humansays explain RULE
humansays config show
humansays config validate [--config PATH]
humansays version
```

A temporary compatibility path may allow bare paths, but documentation should teach `check`.

### 8.2 `check` options

```text
--config PATH
--format terminal|json
--detail findings|signals|all
--symbol NAME
--exclude PATTERN
--fail-on never|advisory|warning|high
--min-score NUMBER
--strict
--timings
```

If `--target-version` is exposed, its limitation must be explicit: it cannot make an older interpreter parse newer Python grammar.

### 8.3 Exit codes

| Code | Meaning |
|---:|---|
| `0` | Analysis completed and no configured gate failed |
| `1` | Finding or score gate failed |
| `2` | CLI or configuration error |
| `3` | No analyzable Python files or required symbol missing |
| `4` | Strict analysis failed because files could not be parsed or analyzed |
| `5` | Internal error |

The exact split may reuse prototype codes, but must be documented and tested before release.

---

## 9. Custom configuration

Custom configuration is required in `0.1.0`.

### 9.1 Supported locations

- explicit path from `--config`;
- `humansays.toml`;
- `.humansays.toml`;
- `[tool.humansays]` in `pyproject.toml`.

Only one discovered base configuration is loaded.

### 9.2 Discovery behavior

- an explicit path must exist and parse successfully;
- discovery begins from the scan root or current working directory;
- `humansays.toml` wins over `.humansays.toml`;
- standalone files win over `pyproject.toml`;
- no parent-directory cascade in v0.1.0 unless explicitly implemented and tested;
- no merging of multiple project files;
- relative exclude paths and referenced files resolve relative to the selected config file.

### 9.3 Precedence

```text
CLI override
    > selected TOML file
    > built-in defaults
```

The prototype's environment-variable support is not required. Retaining it is acceptable only if renamed, documented, and visible in `config show`.

### 9.4 Proposed file

```toml
[selection]
exclude = [
    ".venv",
    "build",
    "dist",
    "generated",
    "migrations",
]

[analysis]
strict = true

[report]
format = "terminal"
detail = "findings"
limit = 100
fail_on = "warning"
min_score = 0.0

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

Unknown sections, keys, rule IDs, and invalid values fail validation.

### 9.5 Config commands

```bash
humansays config validate
humansays config validate --config path/to/humansays.toml
humansays config show
humansays config show --sources
```

`config show` emits the resolved configuration and source of each value where practical.

---

## 10. Internal architecture changes

### 10.1 Do not rewrite the whole prototype

Retain the current layers as a migration starting point:

```text
core
options
models
syntax
py_ast
rules
catalog
scoring
report
```

Refactor toward:

```text
application
config
analysis backend
normalized facts
raw signals
correlated findings
scoring
reporting
```

### 10.2 Required backend seam

Create a backend protocol before adding more rule dependencies on `ast`.

```python
class AnalysisBackend(Protocol):
    name: str
    schema_version: int

    def analyze(
        self,
        files: Sequence[SourceFile],
        options: AnalysisOptions,
    ) -> AnalysisBatch:
        ...
```

### 10.3 Parser-neutral facts

The shared fact model must contain only:

- strings;
- integers;
- floats;
- booleans;
- enums with stable serialized values;
- tuples;
- immutable mappings;
- source spans.

It must not contain `ast.AST`.

Existing `ParsedModule` and `Scope` models may remain backend-internal.

### 10.4 Immutable facts

Once extracted, facts may not be mutated by cohesion or rule evaluation. Existing code that subtracts method names from field-use sets should operate on copies or derived views.

### 10.5 Batch analysis

Even in Python, use a batch-oriented interface. A future Rust implementation can then parse and analyze many files with one native boundary call.

---

## 11. Output contract

### 11.1 Canonical JSON

Example:

```json
{
  "schema_version": 1,
  "tool": {
    "name": "humansays",
    "version": "0.1.0",
    "backend": "cpython-ast"
  },
  "analysis": {
    "requested_files": 14,
    "analyzed_files": 14,
    "failed_files": 0
  },
  "score": {
    "value": 82.4,
    "grade": "B",
    "provisional": true
  },
  "findings": [
    {
      "code": "HS101",
      "title": "Mixed responsibilities",
      "severity": "warning",
      "confidence": 0.84,
      "review_risk": 7.2,
      "location": {
        "path": "src/orders/service.py",
        "start_line": 42,
        "start_column": 0,
        "end_line": 119,
        "end_column": 1
      },
      "evidence": [],
      "constraints": [],
      "suggested_boundaries": [],
      "verification": []
    }
  ],
  "signals": [],
  "errors": []
}
```

Signals may be omitted unless requested, but findings always include their supporting evidence.

### 11.2 Schema rules

- deterministic key and item ordering where applicable;
- relative paths when a stable scan root exists;
- no timestamps in canonical output;
- explicit backend and tool versions;
- versioned JSON Schema checked into the repository;
- golden fixture tests;
- schema changes documented in release notes.

### 11.3 Terminal report

Default terminal output shows findings and compact evidence. `--detail all` shows raw signals and full review questions.

---

## 12. Unit test plan

Use pytest for new tests. Existing `unittest.TestCase` tests may run under pytest during gradual migration.

### 12.1 Required unit suites

```text
tests/unit/
├── test_config_discovery.py
├── test_config_validation.py
├── test_source_spans.py
├── test_function_facts.py
├── test_class_facts.py
├── test_effects.py
├── test_signal_rules.py
├── test_hs101.py
├── test_hs102.py
├── test_hs201.py
├── test_hs202.py
├── test_confidence.py
├── test_scoring.py
├── test_sorting.py
└── test_exit_policy.py
```

### 12.2 Rule test requirements

Each public finding includes:

- positive case;
- negative case;
- threshold boundary;
- counterexample that must not fire;
- evidence ordering;
- confidence calculation;
- configuration override;
- serialization.

### 12.3 Existing test migration

Preserve the 39 existing tests until equivalent coverage exists. Do not delete them merely because pytest has trendier punctuation.

---

## 13. Integration test plan

Integration tests invoke the command through `subprocess`.

Required cases:

- `humansays --help`;
- `humansays version`;
- file scan;
- directory scan;
- stdin newline list;
- stdin NUL list;
- custom standalone config;
- `pyproject.toml` config;
- malformed config;
- nonexistent explicit config;
- CLI override;
- exclusions;
- symbol filtering;
- terminal output;
- JSON output;
- strict parse failure;
- finding gate;
- score gate;
- no-files exit;
- deterministic repeated output.

Tests use temporary repositories rather than only source strings.

---

## 14. Self-scan smoke testing

The project is an ideal smoke-test target for itself.

### 14.1 Source-tree self-scan

Run during normal CI:

```bash
uv run humansays check src/humansays \
  --config humansays.toml \
  --format json \
  --strict
```

Assertions:

- all expected package files are analyzed;
- no parse failures;
- JSON validates;
- no disallowed default-profile findings;
- configured score floor passes;
- output is stable across two runs.

### 14.2 Installed-wheel self-scan

Build the wheel, create a clean environment, install it, then run the installed command against the checked-out `src/humansays` directory.

This proves that:

- console entry points are packaged;
- runtime dependencies are complete;
- no source-tree import masks packaging errors;
- config discovery works;
- the installed CLI can analyze a real package.

### 14.3 Source-distribution self-scan

Install the sdist in a second clean environment and repeat the smoke test.

### 14.4 Self-scan policy

Self-scan is a smoke test, not a correctness oracle.

The gate may use:

- no parse errors;
- no high-severity findings;
- no banned opinionated signals;
- minimum score;
- explicit baseline entries with reasons.

Do not require a permanent score of 100. A stronger future version may legitimately criticize the current implementation.

---

## 15. GitHub Actions

### 15.1 `.github/workflows/ci.yml`

#### Quality job

- Ubuntu 24.04 or `vars.DEFAULT_RUNNER`;
- Python 3.14;
- locked dependency installation;
- Ruff format check;
- Ruff lint;
- `ty check`;
- configuration validation;
- generated-file drift check.

#### Unit matrix

```yaml
python-version:
  - "3.11"
  - "3.12"
  - "3.13"
  - "3.14"
```

Runs all unit and backend fixture tests.

#### Integration matrix

Run CLI subprocess integration tests on Linux for Python 3.11–3.14.

#### Portability

Run focused installation and path tests on:

- `windows-latest`, Python 3.14;
- `macos-latest`, Python 3.14.

#### Package job

After tests:

1. build wheel and sdist;
2. inspect contents;
3. install wheel in a clean environment;
4. run `--help` and version;
5. scan a fixture repository;
6. self-scan;
7. repeat for sdist;
8. upload artifacts.

#### Aggregate job

Expose one stable required check named `CI`.

### 15.2 `.github/workflows/docs.yml`

On pull requests:

- build MkDocs with `--strict`;
- generate finding and config reference;
- fail if generated pages differ.

On `main`:

- repeat build;
- upload Pages artifact;
- deploy with isolated `pages: write` and `id-token: write`.

### 15.3 `.github/workflows/release.yml`

On `v*` tag:

1. verify tag and package version;
2. verify commit belongs to `main`;
3. obtain tested distributions or rebuild deterministically;
4. install both artifacts;
5. run CLI smoke and self-scan;
6. publish to PyPI with OIDC;
7. create GitHub Release;
8. attach wheel and sdist.

### 15.4 `.github/workflows/benchmarks.yml`

Optional in `0.1.0`, recommended immediately after:

- weekly and manual;
- self repository plus pinned corpora;
- upload timing JSON;
- do not block pull requests until baselines stabilize.

---

## 16. Documentation deliverables

The MVP ships:

- README with positioning and quickstart;
- installation guide;
- configuration reference;
- CLI reference;
- finding catalog;
- facts, signals, and findings concept page;
- confidence and limitations page;
- coding-agent integration guide;
- GitHub Actions example;
- architecture page;
- testing and self-scan page;
- future Rust backend note;
- changelog;
- license;
- contributing guide;
- security policy.

MkDocs builds strictly in CI.

---

## 17. Packaging and release requirements

### 17.1 Project metadata

- package name `humansays`;
- `requires-python = ">=3.11"`;
- classifiers for 3.11–3.14;
- project URLs;
- license metadata;
- typed package marker if public APIs are typed;
- `humansays` console entry point;
- lockfile committed for development and CI.

### 17.2 Build backend

Do not switch build backends merely for ceremony. Hatchling may remain for the pure-Python release. `uv_build` is also acceptable if selected intentionally.

A future native extension will likely require Maturin or another native-capable backend.

### 17.3 Release gate

No release occurs unless:

- CI passes;
- docs build;
- wheel installs;
- sdist installs;
- both artifacts pass CLI smoke;
- self-scan passes;
- tag matches version;
- JSON schema tests pass.

---

## 18. Rust-readiness requirements

Rust is not part of `0.1.0`, but the release must avoid making it painful later.

### 18.1 Required now

- backend protocol;
- parser-neutral immutable facts;
- canonical fact serialization;
- backend schema version;
- Python-version syntax fixture corpus;
- golden fact outputs;
- batch backend API;
- no AST nodes in public rules or reports;
- stage-level timing;
- deterministic ordering.

### 18.2 Deferred

- Rust parser selection;
- PyO3;
- Maturin;
- stable ABI wheels;
- native parallelism;
- native cache;
- full Python/Rust parity test matrix.

### 18.3 Future parity gate

A Rust backend cannot become default until:

- all golden facts match or documented differences exist;
- public findings match;
- confidence and score outputs match;
- Python 3.11–3.14 syntax fixtures pass;
- wheels exist for supported platforms;
- performance improvement is material;
- fallback behavior is defined.

---

## 19. Implementation phases

### Phase 1: Freeze prototype behavior

- tag or archive the prototype;
- record 39 passing tests;
- preserve a sample self-scan JSON;
- document current signals and config.

### Phase 2: Rename

- package directory;
- distribution name;
- CLI;
- imports;
- config file names;
- config section;
- environment prefix if retained;
- README;
- schema tool metadata;
- tests.

All existing tests must remain green.

### Phase 3: CI and packaging foundation

- Python 3.11–3.14 metadata;
- lockfile;
- pytest runner;
- GitHub Actions;
- wheel and sdist smoke;
- source-tree and installed self-scan;
- docs skeleton.

### Phase 4: Fact boundary

- split backend-native state from normalized facts;
- remove AST objects from shared models;
- make facts immutable;
- add golden fact serialization;
- add syntax fixtures.

### Phase 5: Findings

- implement `HS101`;
- implement `HS102`;
- migrate cohesion into `HS201`;
- implement `HS202`;
- demote prototype rules to evidence;
- remove noisy defaults.

### Phase 6: Configuration

- public `humansays.toml`;
- discovery;
- rule controls;
- effects configuration;
- validation and introspection;
- integration tests.

### Phase 7: Reporting and documentation

- canonical schema v1;
- detailed terminal output;
- finding docs generated from registry;
- Pages deployment;
- coding-agent examples.

### Phase 8: Release

- release workflow;
- PyPI Trusted Publishing;
- GitHub Release;
- artifact attachment;
- post-publish installation verification where feasible.

---

## 20. Definition of done

Version `0.1.0` is complete only when:

### Product

- package and command are `humansays`;
- four correlated findings exist;
- default output emphasizes findings;
- each finding includes evidence and confidence;
- custom TOML configuration works;
- JSON is stable and versioned.

### Compatibility

- Python 3.11, 3.12, 3.13, and 3.14 pass CI;
- Windows and macOS smoke tests pass;
- runtime parser limitations are documented.

### Tests

- existing prototype coverage is preserved;
- new unit tests cover findings and config;
- subprocess integration tests exist;
- wheel and sdist tests exist;
- self-scan runs from source and installed artifacts;
- strict parse failures are tested;
- golden fact and JSON fixtures exist.

### Delivery

- CI workflow exists;
- docs workflow exists;
- release workflow exists;
- GitHub Pages is configured;
- PyPI Trusted Publishing is configured;
- GitHub Releases attach the exact artifacts.

### Rust readiness

- backend protocol exists;
- shared facts contain no parser-native nodes;
- fact outputs are canonical and golden-tested;
- batch analysis boundary exists;
- stage timings exist.

---

## 21. Post-MVP priorities

Recommended order:

1. evaluate false positives on labeled real code;
2. add base/head structural comparison;
3. add structural-regression finding;
4. add cosmetic-refactor detection;
5. add repository baselines;
6. add SARIF and GitHub annotations;
7. add cache;
8. benchmark larger projects;
9. decide whether Rust is justified;
10. add editor integration only after latency and schema stability.

The MVP should leave a credible instrument, not a pile of 22 renamed opinions wearing a new logo.
