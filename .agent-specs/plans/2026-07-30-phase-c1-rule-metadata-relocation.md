# Phase C1 — rule metadata relocation

> **Executed and superseded, 2026-07-30.** The work landed on branch
> `chore/rules-relocation`. The **Context** and **Established Facts** sections
> below describe the tree *before* this plan ran: `src/humansays/catalog.py` and
> `src/humansays/signals/` were deleted by it and no longer exist. Read them as
> a record of what the author found, not as a description of the current
> layout. Phase C2 followed and is in
> `2026-07-30-phase-c2-disposition-model.md`.

## Context

Rule metadata lives in Python today. `src/humansays/catalog.py` holds a
19-entry `RULES` table of `RuleSpec` literals, and each rule's observation text
is an f-string buried in a `signals/` module. Changing a weight or a message
means editing code, and the grouping of `signals/` follows the *shape of fact
consumed* (`signature.py`, `shape.py`, `structure.py`) rather than the domain
a rule belongs to — `structure.py` alone holds rules that belong to three
different domains.

C1 relocates that metadata into per-group TOML data files and reorganizes the
detection code into rule-group packages, so a reader opening
`humansays/rules/kiss/` sees the definitions and the detection side by side.

**C1 changes no behavior.** All 19 `HS0NN` identifiers stay exactly as they
are, no rule is added or removed, no threshold, severity, confidence or weight
changes, and every observation and evidence string stays byte-identical. The
verification is a plain byte diff against a baseline captured before the
change, which must be empty.

### Why the original Phase C plan was re-scoped

The source plan asked to migrate identifiers onto the new domain scheme in the
same change, citing `docs/site/planned/reconciliation.md` as the authority. That
document does not describe a rename. Of the 19 shipped rules it maps only four
as pure renames; ten are demoted to hidden `evidence`, three to unweighted
`hint`, and three split across multiple identifiers. Applying it would remove 13
rules from scoring, which is irreconcilable with the plan's own invariants 1 and
2. `hint` and `evidence` do not exist in the codebase.

The work therefore splits three ways, and **this plan is C1 only**:

| | Scope | Verification |
|---|---|---|
| **C1** | Relocation: TOML definitions, adapter protocol, registry, `rules/<group>/` layout. Identifiers unchanged. | Empty byte diff |
| **C2** | Disposition model: `on \| hint \| evidence \| off` as a field distinct from `Severity`, plus `--show-evidence`, the review profile, and evidence citation. | New behavior, own tests |
| **C3** | Reconciliation: apply the mapping. Rename 3, demote 10, demote 3, split 3. | Agreement with the reconciliation table |

C3 depends on C2 because 13 of the 19 target identifiers are only expressible
once `evidence` and `hint` exist.

### Decisions taken

- **Rule definitions are a package artifact**, not a user extension point.
  Users tune thresholds through `humansays.toml`; they never author rule files.
  Thin `tomllib` loader, validation in CI over files we ship. `dependencies`
  stays `[]`.
- **Only observation messages move into TOML.** Evidence construction stays in
  adapter code. Evidence has four incompatible shapes — raw pass-through,
  fixed single line, variable-length one-per-item, and conditional (`HS003` at
  `shape.py:49-53` appends a second line only when `facts.class_name` is set).
  The conditional case cannot be expressed without a predicate in data, which
  the no-logic-in-data constraint forbids. Rather than ship "evidence is in
  TOML except when it isn't", none of it moves.
- **`SignalName` is untouched.** It is used in `analysis/body_visitor.py`,
  `analysis/accumulators.py`, `facts/values.py`, `reporting/grouping.py` and
  `findings/models.py` — five modules outside the rules layer. It remains the
  identifier type and the `RULES` key, which preserves the fail-fast property
  `catalog.py:3-5` describes for free.
- **Group directory comes from the domain prefix of reconciliation's New ID
  column; the identifier does not change.** `HS003` lives in `rules/kiss/` and
  keeps the id `HS003`. Where a row splits, the domain of the primary target
  is used. The two-namespace problem does not arise in C1 because nothing
  renames.

## Invariants

| # | Invariant | Enforcer |
|---|---|---|
| 1 | Output is byte-identical on every fixture, both formats, color on and off. | `.migration/capture.sh` diff (Task 8); `tests/golden/test_self_scan.py`; `tests/golden/test_parity.py`; `tests/unit/test_rule_definitions.py::test_specs_match_frozen_metadata` |
| 2 | Every id in a `rules.toml` is registered, and every registered id exists in a `rules.toml`. | `tests/unit/test_rule_registry.py::test_definitions_and_registry_agree` |
| 3 | Every `{placeholder}` in a message template is supplied by its adapter payload, and every payload key is consumed. | `tests/unit/test_rule_messages.py::test_message_placeholders_match_payloads` |
| 4 | Adapter order is explicit, not import- or filesystem-derived. | Literal tuples in `rules/registry.py`; `tests/unit/test_rule_registry.py::test_registry_order_is_literal` |
| 5 | Nothing under `humansays.rules` imports `ast`, `tokenize`, or `humansays.analysis`. | `lint-imports` contracts `ast-confined-to-analysis` and `layers`; `tests/integration/test_analysis_confinement.py`; `tests/integration/test_import_contract_coverage.py` |
| 6 | Zero runtime dependencies. | `deptry` in `scripts/lint.sh`; `dependencies = []` |

Do not describe any of these as enforced without naming the check above.

## Established facts

Verified against the tree. Re-run rather than trust.

- `catalog.py` holds `RULES: MappingProxyType` keyed by `SignalName`, 19
  entries, plus `WARNING_WEIGHT = 3.0`, `ADVISORY_WEIGHT = 1.0`, and an unused
  `NOTICE_WEIGHT = 0.0` (leave it; it is C2's tier). `build_finding` at
  `catalog.py:213` is the single construction site.
- `catalog` is imported by exactly six `signals/` modules and
  `tests/unit/test_deleted_rules.py:10`. Small blast radius.
- `RuleSpec` is defined in `findings/models.py:49-69`, not in `catalog.py`.
  `check_bounds` at `findings/models.py:19` validates confidence and weight in
  `__post_init__` — reuse it, do not write a second bounds checker.
- **`RuleSpec` is serialized field-for-field into the JSON report.**
  `reporting/grouping.py:84` calls `dataclasses.asdict(finding.rule)` and
  `RuleView` (lines 16-23) enumerates the five fields; the comment at lines
  79-81 warns that both must be edited together. **Adding any field to
  `RuleSpec` adds a key to every JSON signal object and breaks invariant 1.**
  The message template therefore lives on a `RuleDefinition` wrapper that
  *holds* a `RuleSpec`; `RuleSpec` gains nothing.
  (`field_values` at `findings/models.py:25` is applied only to `Score`, so
  checking it alone is not sufficient — the direct `asdict` is the live path.)
- **`review_question` never reaches text output.** Only `create_signal` reads
  it, so it appears only in JSON. `tests/unit/test_text_snapshot.py` cannot
  catch a seam error in a review question — which is why the frozen-literal
  test below is load-bearing rather than belt-and-braces.
- `tests/golden/poc-parity/corpus/poc/catalog.py` is a vendored independent
  oracle carrying all 19 review questions as single-line literals (verified: 22
  `review_question=` entries, keyed `PY0NN`, mapped to `HS0NN` by
  reconciliation's Prototype column). A free cross-check for the seam risk.
- `Finding.sort_key` is `(location.line, rule.rule_id)`;
  `evaluation.py:58` sorts with `sorted`, which is stable.
- Module line counts: `structure.py` 110 (largest), `shape.py` 78,
  `cohesion.py` 73, `effects.py` 69, `signature.py` 67, `evaluation.py` 58,
  `scope.py` 38.
- `.importlinter.ini` `layers` places `humansays.catalog` **below**
  `humansays.analysis | humansays.signals`. `ast-confined-to-analysis`
  enumerates all seven `humansays.signals.*` modules by name (lines 44-51) and
  also lists `humansays.catalog` (line 21).
- **The two contract stanzas have two different enforcers**, verified by
  experiment:
  - A missing or stale entry in `ast-confined-to-analysis` fails
    `tests/integration/test_import_contract_coverage.py`, which derives the
    expected list from the filesystem and asserts both directions. It reads
    *only* that contract (`CONTRACT` at line 18), so it does **not** cover the
    layers stanza.
  - A stale module in the `layers` stanza fails `lint-imports` itself:
    injecting `humansays.ghostmodule` produced
    `Missing layer 'humansays.ghostmodule': module ... does not exist` and
    **exit code 1**.
- `.migration/` is gitignored (`.gitignore:225`). Phase B's capture script is
  at `.agent-specs/plans/2026-07-29-phase-b-extraction-split.md:288-303`;
  reuse it verbatim with a new output directory.
- `pyproject.toml`: `uv_build>=0.11.32,<0.12.0`, `requires-python = ">=3.11"`,
  `dependencies = []`, no `[tool.uv.build-backend]` section, so packaging
  defaults apply and **whether `*.toml` ships must be tested, not assumed**.
  The 3.11 floor rules out PEP 695 generic syntax.
- `pytest-randomly` is enabled, so test order is randomized between runs. Any
  test that samples must carry an explicit seed.
- `.coveragerc.ini` sets `fail_under = 85`; loader error paths need tests or
  the gate drops.

## Discovered during execution

- **Tasks 4 and 5a had to swap.** As sequenced, Task 4 puts `registry.py` in
  `humansays.rules` while the adapters it imports are still in
  `humansays.signals`. But `signals/*` already imports `rules.models` for
  `Emission`, so the two packages would import each other: a layer inversion
  under the `layers` contract and a cycle under `acyclic-package` at depth 2.
  There is no ordering of the two contracts that permits it. Moving first
  dissolves it, because afterwards every adapter and the registry are inside
  `humansays.rules`. Executed order:
  1. uniform adapter signatures `(facts, thresholds)` in `signals/`
  2. verbatim move into `rules/<group>/`, `catalog.py` deleted (was 5a)
  3. `protocol.py` + `registry.py` + `evaluation.py` rewrite (was 4)
  4. split the bundled adapters (5b)
  Each still ends on an empty byte diff, and the verbatim move is still
  isolated from any behavioral change, which is what splitting 5 was for.

  **The general form of the error, for the next phase's plan to be checked
  against:** the plan assigned modules to packages without checking the import
  direction that already existed between them. A task sequence that creates a
  module in package A while the things it imports still live in package B is
  unexecutable whenever B already imports A, and no ordering of the contracts
  rescues it. Before sequencing tasks that move code between packages, read the
  current edges in both directions, not just the ones the target layout wants.

- **C1's own gate reported success while C1 was breaking a test.** The
  interpreter-version survey in `tests/integration/test_analysis_confinement.py`
  named the packages `('facts', 'signals')`. Task 5a renamed `signals` to
  `rules`; `rglob` over a directory that does not exist yields nothing rather
  than raising, so the survey went on passing while scanning half of what its
  name claimed. This was not pre-existing. C1 broke it, and the full gate — 286
  passing, lint green, `deptry` clean, byte diff `IDENTICAL` at all seven
  commits — was green throughout.

  The reason generalizes past this bug, and is the thing to carry forward.
  **Byte-identical output proves the analyzer behaves the same. It says nothing
  about whether the tests still test the same things.** Coverage cannot reach
  it either: a test that reads source files *as data* does not move a covered
  line when its input set halves. There is no passive signal for this class of
  defect, which is why CLAUDE.md "Always" 14 has to be applied deliberately
  rather than merely recorded. `tests/fixtures/sweeps.py` is the mechanism —
  every file sweep in the suite goes through it and an empty result raises —
  but a mechanism only covers the sweeps that were routed through it.

- **The self-scan is a second, independent constraint the plan missed.**
  `tests/golden/test_self_scan.py` is exact-match against
  `src/humansays`, so any new or moved module that produces a weighted finding
  fails it. All six baseline entries point at `cli.py` and `reporting/ansi.py`
  — none at `signals/` or `catalog.py` — so moving those modules is safe, but
  new code under `src/` must produce zero weighted findings or the baseline
  needs an entry with a reason. Verified green after Tasks 2 and 3.
- **`uv_build` does ship `*.toml` under `src/`** with no
  `[tool.uv.build-backend]` section. Wheel contains all eight
  `humansays/rules/<group>/rules.toml`; a real venv install resolves them
  through `importlib.resources`. Locked in by
  `tests/tooling/test_package_data.py`.
- **All 19 review questions match the vendored prototype oracle exactly**
  (`tests/golden/poc-parity/corpus/poc/catalog.py`, `PY0NN` → `HS0NN` by
  number). `test_review_questions_match_poc_oracle` now holds it.
- **HS005 has no microfixture** anywhere under `tests/fixtures/`. It is
  observed only in the self-scan baseline against humansays' own source. This
  is a pre-existing gap against CLAUDE.md "Always" rule 9, not one C1 created.
  `test_rule_messages.py` supplies its own broad-except snippet rather than
  widening C1's scope. Report it; do not fix it here.
- `.ruff.toml` gained a per-file `E501` ignore for
  `tests/unit/test_rule_definitions.py`: the frozen review questions must stay
  unbroken single-line literals, since wrapping them would reintroduce the
  implicit-concatenation seams the table exists to catch.

## Group assignment

Nineteen rules, eight groups. Domain from reconciliation's New ID column.

| Group | Rules |
|---|---|
| `contract` | HS001, HS014 |
| `solid` | HS002, HS007, HS008, HS012, HS013, HS018 |
| `kiss` | HS003, HS009, HS017, HS019, HS022 |
| `encap` | HS004, HS006 |
| `err` | HS005 |
| `yagni` | HS015 |
| `smell` | HS016 |
| `idiom` | HS021 |

## Target layout

```
src/humansays/rules/
├── __init__.py          re-exports evaluate
├── models.py            RuleDefinition, Emission, Adapter
├── loading.py           TOML load, strict key + placeholder validation
├── protocol.py          per-scope adapter protocols
├── registry.py          literal ordered tuples, merged definitions, build_finding
├── evaluation.py        the walk
├── contract/  rules.toml  adapters.py            HS001+HS014
├── solid/     rules.toml  signature.py           HS002
│                          effects.py             HS007
│                          cohesion.py            HS008
│                          class_shape.py         HS012, HS013, HS018
├── kiss/      rules.toml  adapters.py            HS003, HS009, HS017, HS019, HS022
├── encap/     rules.toml  adapters.py            HS004, HS006
├── err/       rules.toml  adapters.py            HS005
├── yagni/     rules.toml  adapters.py            HS015
├── smell/     rules.toml  adapters.py            HS016
└── idiom/     rules.toml  adapters.py            HS021
```

`solid/` is split across four modules because a single one would run ~164
lines, well past the 110-line high-water mark set by `structure.py`. Every
module above lands under 110; report the real number at the end (Task 8).

## Definition format

One `rules.toml` per group. A rule entry carries exactly six keys: `id`,
`severity`, `confidence`, `weight`, `message`, `review_question`. No detection
logic, no conditions, no thresholds — thresholds stay in `config/models.py`,
where users already reach them through `humansays.toml`.

```toml
# rules/solid/rules.toml
[[rule]]
id = "HS018"
severity = "warning"
confidence = 0.78
# WARNING_WEIGHT: multiple parents make the MRO the real design.
weight = 3.0
message = "Class inherits from {count} parent classes."
review_question = """\
Is this composition, mixin layering, or an inheritance chain \
that hides the real collaborators?"""
```

The adapter for HS018 returns payload `{"count": len(bases)}` and evidence
`bases`; the framework renders the message.

`RULE_KEYS` is a frozen set of exactly those six names, and the loader rejects
any key outside it. That is the enforcer for "no logic in data": a `when`,
`threshold` or `min_lines` key is a hard error at load, and no field exists on
`RuleDefinition` that could hold a condition.

Use the line-ending-backslash continuation form shown above for every
`review_question`, uniformly. TOML strips the newline *and* all leading
whitespace after the backslash, so the seam space must be typed **before** the
backslash — exactly where Python's implicit concatenation puts it. That makes
the transliteration mechanical.

### Byte-identity hazards

The highest-risk part of this phase is the concatenation seams. Several
messages and every `review_question` are currently adjacent implicitly-
concatenated string literals, and a dropped or doubled space produces a message
wrong by one byte that looks right in review. Verified seams, character by
character:

| Rule | Source | Renders as |
|---|---|---|
| HS013 | `structure.py:88-89` | `...{count} repeated attribute-prefix clusters.` |
| HS004 | `scope.py:32-33` | two placeholders; backticks around the name are literal in TOML |
| HS006 | `effects.py:44-45` | `...{count} independent state owners.` |
| HS007 | `effects.py:62-63` | `...{count} standard-library boundary categories.` |
| HS008 | `cohesion.py:68-69` | `...{count} disconnected field-access clusters.` |
| HS015 | `structure.py:54-55` | `...neither instance nor class state.` |

Five rules have no placeholders at all: HS002, HS005, HS015, HS016, HS021. The
other fourteen each take a single scalar except HS004, which takes two. Payload
for the five static rules is an empty mapping, and the coverage check passes on
empty-both-sides rather than special-casing them.

Render strictly, because `str.format` silently ignores extra kwargs:

```python
def render(template: str, keys: frozenset[str], payload: Mapping[str, object]) -> str:
    if payload.keys() != keys:
        raise ValueError(
            f'payload keys {sorted(payload)} do not match placeholders {sorted(keys)}'
        )
    return template.format(**payload)
```

The loader also rejects positional fields (`{0}`, `{}`), attribute and index
access (`{a.b}`, `{a[0]}`), conversions (`{x!r}`) and format specs (`{x:>3}`),
so a template can only ever name plain identifiers.

## Design decisions

### Where the loader lives, and the import cycle it avoids

`humansays.catalog` sits *below* `humansays.signals` in the layers contract,
so the obvious move — have `catalog.py` read the TOML — inverts the layer.
Worse, `importlib.resources.files('humansays.rules.kiss')` imports that
subpackage, and the subpackage needs `build_finding`, which is a cycle at the
depth-2 `acyclic-package` contract.

Both problems dissolve with two choices:

1. Address package data as `files('humansays.rules').joinpath(group, 'rules.toml')`.
   Traversal into a subdirectory does **not** import the subpackage, so only
   the parent package is imported.
2. Make the load lazy and cached (`@cache`) rather than a module-level
   constant. Nothing loads at import time, so no partially-initialized-module
   subtlety exists.

The resulting graph inside `humansays.rules` is acyclic: `models` and `loading`
import nothing internal; each group's adapters import `models`; `registry`
imports `loading` and the groups; `evaluation` imports `registry`.

`catalog.py` is deleted and `RULES` / `build_finding` move to
`rules/registry.py`.

### Fail-fast on an unknown identifier

Preserved unchanged and for free. `RULES` stays keyed by `SignalName`, so
`RULES[SignalName.HS018]` is still the only way to reach a spec and a typo is
still an immediate `KeyError`. Carry the `catalog.py:1-6` docstring across.
Additionally the loader raises, naming file, id and field, when a TOML `id` is
not a `SignalName` member, when an id is duplicated within or across groups,
when a required key is missing, or when an unknown key is present. Merging also
raises if any `SignalName` member has no definition, so the map is total.

### Adapter protocol

Scopes derived from `evaluation.py`, not assumed: `MODULE`, `FUNCTION`,
`CLASS`, `METHOD`, plus the module-level lambda pass. `FUNCTION` adapters run
on both module-level functions and methods; `METHOD` adapters (only
`static_method`/HS015) run on methods alone.

Signatures are uniform *within* a scope and deliberately not unified across
scopes — collapsing them into one `evaluate(facts)` reintroduces the dispatch
Phase B removed:

```python
class ModuleAdapter(Protocol):
    rule_ids: frozenset[SignalName]
    def __call__(self, facts: ModuleFacts, thresholds: Thresholds) -> list[Emission]: ...

class FunctionAdapter(Protocol):
    rule_ids: frozenset[SignalName]
    def __call__(self, facts: FunctionFacts, thresholds: Thresholds) -> list[Emission]: ...

class ClassAdapter(Protocol):
    rule_ids: frozenset[SignalName]
    def __call__(self, facts: ClassFacts, thresholds: Thresholds) -> list[Emission]: ...
```

Each adapter takes the whole `Thresholds` and selects the slice it needs, and
returns `Emission` values — signal, location, scalar payload, finished evidence
tuple — rather than `Finding`s. The pipeline assembles. That is what keeps
adapters from needing the registry, which is what breaks the cycle.

### Registration and order

No decorators, no `pkgutil` scan, no `__subclasses__`. `registry.py` holds one
literal tuple per scope. A literal tuple in a single file is stronger than
sorting a decorator scan: explicit, diffable, and unable to depend on import or
filesystem order.

### Why reordering adapters is safe

This argument licenses reorganizing the walk, so state it in the PR.

`sorted` is stable and `sort_key` is `(line, rule_id)`. Two findings compare
equal only when they share *both* line and rule id. A stable sort's output is
determined by the multiset of keys, the key-to-element mapping, and the input
order of elements sharing a key. Permuting adapters changes none of the first
two. For the third, findings sharing a key must come from the same adapter
invocation — and an adapter's internal loop is untouched by the move.

> **Adapter order within a scope instance is free. The scope-instance walk
> order is not.**

The walk in `evaluate`, `class_signals` and `function_signals` must be
preserved exactly: module work before functions, functions before classes,
lambdas last, class methods in source order, and the class head/tail phases
either side of the method loop. Ties actually occur — HS005 and HS021 emit
several findings at one function location, and two lambdas can share a line.

The condition holds for HS004's two registrations because module-scope
bindings and class-body bindings occupy disjoint source lines. That is a
property of Python's grammar, not of the type system, so measure it rather
than assert it: `test_no_two_adapters_share_a_sort_key` collects
`(sort_key, adapter_name)` across every fixture and the corpus and asserts each
key maps to one adapter.

### Bundled adapters that now span groups

- `argument_signals` emits HS001, HS014 (contract) and HS002 (solid). HS014 is
  emitted *inside* the HS001 branch (`signature.py:28`), so HS001+HS014 stay
  one adapter in `contract/`. HS002 is independent and becomes its own adapter
  in `solid/signature.py`.
- `incident_signals` emits HS005 (err) and HS021 (idiom) from one comprehension
  over `facts.body.incidents`. Split into two adapters, each reading
  `.get(signal, ())`. The hand-maintained `INCIDENT_MESSAGES` map at
  `effects.py:11-14` dissolves into the two groups' TOML — the clearest win of
  the refactor.
- `state_signals` emits HS006 (encap) and HS007 (solid) from two independent
  `if` blocks. Trivial split.
- `class_state_surface` emits HS013 only inside the branch that emits HS012
  (`structure.py:62-95`). Both are `solid`. Keep them as **one adapter
  declaring two rule ids** — splitting would duplicate the
  `len(attributes) > max_attributes` gate and the clustering call, and the
  drift failure mode (HS013 firing without HS012) is caught by no existing
  fixture.

### HS004: two adapters, one implementation

`mutable_bindings` is invoked at module scope (`evaluation.py:49`) and class
scope (`evaluation.py:34`). One callable cannot satisfy both protocols —
`ModuleAdapter` takes `ModuleFacts`, `ClassAdapter` takes `ClassFacts`. So it
becomes two thin adapters delegating to one shared helper:

```python
# rules/encap/adapters.py
def _bindings(bindings, symbol, scope) -> list[Emission]:
    return [
        Emission(SignalName.HS004, Location(symbol, b.line, b.end_line),
                 {'scope': scope, 'name': b.name},
                 (f'{b.name} initialized as {b.constructor}',))
        for b in bindings
    ]

def module_shared_state(facts: ModuleFacts, thresholds: Thresholds) -> list[Emission]:
    del thresholds
    return _bindings(facts.bindings, '<module>', 'module')

def class_shared_state(facts: ClassFacts, thresholds: Thresholds) -> list[Emission]:
    del thresholds
    return _bindings(facts.bindings, facts.name, 'class')
```

(`del thresholds` is the house idiom for an unused required argument; see
`tests/conftest.py:33`.) The detection stays single-sourced, the protocols stay
honest, and the three-way set equality below is unaffected.

### The completeness invariant

Two rules are declared by an adapter that declares two ids (HS001+HS014,
HS012+HS013), and HS004 is declared by two adapters. So the relation is
many-to-many, bounded by an explicit allowlist rather than asserted as a
bijection:

```python
MULTI_ADAPTER_RULES = frozenset({SignalName.HS004})   # module scope and class scope
MULTI_RULE_ADAPTERS = {
    'contract.argument_contract': (SignalName.HS001, SignalName.HS014),
    'solid.class_state_surface':  (SignalName.HS012, SignalName.HS013),
}

declared = {(a.name, s) for a in ALL_ADAPTERS for s in a.rule_ids}
assert {s for _, s in declared} == set(DEFINITIONS) == set(SignalName)
assert {s for s, n in Counter(s for _, s in declared).items() if n > 1} == MULTI_ADAPTER_RULES
assert {a.name: a.rule_ids for a in ALL_ADAPTERS if len(a.rule_ids) > 1} == MULTI_RULE_ADAPTERS
```

The allowlists are the point: growth of the many-to-many relation becomes a
deliberate edit with a comment, not drift. Also assert no adapter declares an
id from another group, and no id is defined in two groups.

## Tasks

Each task ends green — full suite and `scripts/lint.sh` pass, and the byte diff
is empty. Run `scripts/format.sh` before `scripts/lint.sh`; never invoke ruff
or ty directly. Commit at the end of each, saying what changed and what did not.
Conventional commits per `scripts/check_commit_msg.py`: `chore(rules): ...`,
lowercase summary, no trailing period.

**Task 1 — baseline.** Cut `chore/rules-relocation` off `develop`. Git state is
settled with the operator: the uncommitted one-blank-line change at
`scripts/check_commit_msg.py:47` rides along untouched and must never enter a C1
commit, and `stash@{0}` (from `fix/prerelease-bugs`) stays unapplied. Stage
files by explicit path; never `git add -A` or `git commit -a`.
Copy Phase B's capture script to `.migration/capture.sh`, capture
into `.migration/phase-c1-baseline/`, capture again into a recheck directory,
and `diff -r`. A non-empty diff means pre-existing nondeterminism — stop and
report, because every later step depends on this artifact. Record that
`uv run pytest` and `scripts/lint.sh` pass at the branch point.

**Task 2 — definitions alongside catalog.** Add `rules/models.py`,
`rules/loading.py` and the eight `rules.toml` files. `RuleDefinition` wraps a
`RuleSpec` and adds `message` and `placeholders`; **`RuleSpec` gains no
fields**. Nothing switches over yet. Add
`tests/unit/test_rule_definitions.py::test_toml_matches_catalog` asserting the
loaded specs equal `catalog.RULES` field by field — this proves the
transcription before any behavior can change. Add the loader error-path tests
(unknown key, missing key, unknown id, duplicate id, out-of-range confidence,
positional field, conversion, format spec) to hold coverage above 85. Add the
packaging test: build a wheel, install it into a temp venv, and load every
group through `importlib.resources` — `uv_build` shipping `*.toml` is
unverified and would otherwise fail only after publish.

**Task 3 — flip authority.** Point `build_finding` at the loaded definitions,
delete `RULES` from `catalog.py`, and convert each adapter to return an
`Emission` with a payload instead of an f-string. Add the placeholder-coverage
test.

Replace — do not delete — the dual-source test from Task 2. Once `catalog.RULES`
is gone, the byte diff only covers rules that actually fire on the golden
corpus, leaving any non-firing rule's severity, confidence, weight and
`review_question` unverified from here on. `review_question` is especially
exposed because it reaches JSON only, so `test_text_snapshot.py` cannot see it.
So `test_toml_matches_catalog` becomes
`test_specs_match_frozen_metadata`: the same field-by-field assertion against
**literals frozen in the test file**, copied verbatim out of today's
`catalog.py`. Same protection, no dependency on `catalog.RULES`. Add
`test_review_questions_match_poc_oracle` as a second, independent check parsing
`tests/golden/poc-parity/corpus/poc/catalog.py`; verify it passes before
committing it, and drop it rather than "fixing" a string if any legitimately
diverged.

Verify: empty diff.

**Task 4 — protocol and registry.** Add `protocol.py` and `registry.py`,
rewrite `evaluation.py` to walk facts in the current order and run each scope's
registered adapters against literal tuples. Adapters still live in `signals/`.
Verify: empty diff.

**Task 5a — move modules verbatim.** Move the seven `signals/` modules into
`rules/<group>/` with **no splitting** — each file moves whole to the group of
its first-listed rule, imports updated, contents otherwise untouched. Delete
`catalog.py`. Update `.importlinter.ini` (see below), test imports (`from
humansays.signals import evaluate` appears in several files) and
`tests/unit/test_deleted_rules.py:10`. Verify: empty diff.

**Task 5b — split the bundled adapters.** Split `argument_signals`,
`incident_signals`, `state_signals` and `mutable_bindings` per the design
above, moving the pieces to their target groups. Verify: empty diff.

Splitting 5 in two matters because a non-empty diff in a combined task gives no
bisect signal — a move and a behavioral split would be indistinguishable.

**Task 6 — invariant tests.** Completeness with the two allowlists;
`test_no_two_adapters_share_a_sort_key`; determinism across repeated evaluation
and across separate process invocations, since `pytest-randomly` is on; an
adapter-permutation test with an explicit `random.Random(0)` seed; registry
order as literal tuples; walk-order frozen against a fixture exercising module
scope, a module function, a class with a method, and a lambda.

**Task 7 — `.importlinter.ini` and docs.** Confirm both contracts are clean:
- `ast-confined-to-analysis`: drop `humansays.catalog` (line 21) and the seven
  `humansays.signals.*` entries; add every new `humansays.rules.*` **module**
  (the eight `rules.toml` files are data and must not appear). Enforcer:
  `tests/integration/test_import_contract_coverage.py`, both directions.
- `layers`: change `humansays.analysis | humansays.signals` to
  `humansays.analysis | humansays.rules`, keeping the `|` — the comment at
  lines 57-60 explains it bans the dependency both ways — and **delete the
  `humansays.catalog` line**, since the module is gone. Enforcer: `lint-imports`
  itself, which exits 1 with `Missing layer ...: module ... does not exist`.
  The coverage test does **not** cover this stanza.
- Update the prose comment at lines 57-60, which says "signals".

Also update `docs/site/rules/index.md` (it names `catalog.py`, `RuleSpec`'s
fields, and the weight constants) and `docs/site/planned/reconciliation.md:4`
(the path). No new page, so no `mkdocs.yml` nav edit.

**Task 8 — verify and ship.** Full suite and `scripts/lint.sh`. Show the capture
command and its empty diff in the PR — do not claim it without showing it. Name
each `lint-imports` contract individually. Confirm `deptry` reports no
undeclared imports and `dependencies` is still `[]`. Report the largest module
under `rules/` and flag it if over 110 lines. Delete `.migration/`. Open a PR
with the repository template, recording the package-artifact decision, the
messages-only-in-TOML decision, the HS004 and multi-id allowlists, and the
C1/C2/C3 split with the reconciliation finding that forced it.

## Verification

```bash
# Baseline, before any change
.migration/capture.sh .migration/phase-c1-baseline

# After each task
.migration/capture.sh .migration/phase-c1-check
diff -r .migration/phase-c1-baseline .migration/phase-c1-check && echo "IDENTICAL"
rm -rf .migration/phase-c1-check

uv run pytest
scripts/format.sh && scripts/lint.sh
```

`IDENTICAL` is the pass condition for invariant 1 at every task. Anything else
means stop and report, not adjust the baseline.

Packaging is verified separately, because the source tree cannot prove it:

```bash
uv build
# install the wheel into a scratch venv and load every group through
# importlib.resources; a missing rules.toml fails only after publish otherwise
```

## Out of scope

New rules; caching; the three-per-group breadth work; any change to detection
logic, thresholds, severities, confidences or weights; identifier migration;
`hint`/`evidence` dispositions; retiring `SignalName`; moving threshold
defaults out of `config/models.py`.

If a step cannot be completed as written, stop and report. Do not substitute an
approach.
