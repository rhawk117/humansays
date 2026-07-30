# Phase B — Extraction / Evaluation Split Implementation Plan

> **Superseded.** This work landed as commit `41ceb74`, "refactor(analysis):
> split RulesetEvaluator into extraction, facts, and signals (#19)", which went
> further than planned — `signals/` is already split per rule group, which this
> plan deferred to Phase C. Kept for provenance; do not execute it. The gaps
> found reviewing the merged result are tracked in
> `2026-07-29-extraction-enforcer-gaps.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split `RulesetEvaluator` into an extraction layer that owns the AST and an evaluation layer that sees only plain data, with output unchanged.

**Architecture:** Three packages. `humansays.facts` holds pure dataclasses and imports no `ast`. `humansays.analysis` keeps the AST and gains one entry point, `extract_module_facts(ParsedModule) -> ModuleFacts`, that walks the tree once. `humansays.signals` consumes `ModuleFacts` and emits `Finding` objects, and may import neither `humansays.analysis` nor `ast`. `application.analyze_file` orchestrates parse → extract → evaluate. `import-linter` enforces every boundary.

**Tech Stack:** Python 3.11+ (`requires-python = ">=3.11"`), stdlib only, `uv` for everything, `pytest`, `ruff`, `ty`, `import-linter`, `deptry`, `vulture`.

## Global Constraints

- **Zero runtime dependencies.** `dependencies = []` in `pyproject.toml` stays empty. `deptry` (`scripts/lint.sh deps`) is the enforcer. No extras.
- **No `ast` or `tokenize` outside `humansays.analysis`** — and never in `humansays.facts` or `humansays.signals`, including temporarily mid-refactor.
- **Absolute imports inside `src/humansays`.** `from humansays.config import ...`, never `from .config import ...`. `TID252` via `.ruff.toml` `ban-relative-imports = "all"` is the enforcer; `scripts/format.sh` rewrites violations in place.
- **Output must not change** for the poc-parity corpus: not formatting, wording, finding order, or JSON key order.
- **No new rules, no removed rules**, no changed thresholds, severities, confidences, or weights.
- **No per-rule-group module layout**, no rule definition files, no `RuleGroupDefinition`, no adapter protocol. Phase C.
- **No caching implementation.** Task 8 constrains the design only.
- **No second tree walk** added for any rule.
- **Two severities only:** `WARNING` weight 3.0, `ADVISORY` weight 1.0.
- **Run `scripts/format.sh` before `scripts/lint.sh`.** Never invoke `ruff`/`ty`/`deptry`/`lint-imports` directly. `scripts/format.sh` is the only quality script that writes to the repo.
- **Every enforcement claim names its enforcer.** If no test, hook, or CI job proves it, write it as convention.
- **The operator owns git beyond this branch.** Commit as the plan directs; do not push, merge, or create further branches.
- **If a step cannot be completed as written, stop and report.** Do not substitute an approach.

---

## Facts Established During Planning

Every claim below was verified against the tree. The command that proves it is
given so the implementer can re-run it rather than trust this document. Several
contradict the source spec — those are called out.

### The source spec is wrong about five things

```bash
# 1. tests/cli/ does not exist. Invariant 5 names a nonexistent enforcer.
ls tests/cli/
#   ls: cannot access 'tests/cli/': No such file or directory

# The real exit-code enforcer:
ls tests/integration/test_exit_contract.py
grep -n 'exit_code' tests/integration/test_exit_contract.py
#   162:    assert payload['status']['exit_code'] == 5
#   173:        'exit_code': 0,

# 2. tests/parity/ does not exist. The parity test lives under tests/golden/.
ls tests/parity/
#   ls: cannot access 'tests/parity/': No such file or directory
ls tests/golden/
#   __pycache__  poc-parity  self-scan-baseline.json  test_parity.py  test_self_scan.py

# 3. Phase A left reporting/ with nine modules, not the four the spec names.
ls src/humansays/reporting/
#   __init__.py ansi.py console.py grouping.py models.py payload.py render.py renderers.py terminal.py

# 4. There are zero sys.version_info branches to consolidate.
grep -rn 'version_info' src/ tests/ scripts/ ; echo "exit=$?"
#   exit=1        (no matches)

# 5. tests/golden/test_self_scan.py scans src/humansays ITSELF.
grep -n 'SRC_ROOT' tests/golden/test_self_scan.py
#   17:SRC_ROOT = 'src/humansays'
#   21:    Selection(paths=(SRC_ROOT,))
```

Consequences of 4 and 5 are decided below under **Scope Decisions**.

### The source spec is right about two things

```bash
# Scope.node is read nowhere in src/. The only .node read is FunctionTarget.node.
grep -rn '\.node' src/
#   src/humansays/analysis/python_ast.py:321:    node = target.node
# => dropping Scope.node is free.

# module_scale_findings builds Finding objects inside the extraction module.
sed -n '249,263p' src/humansays/analysis/python_ast.py
#   def module_scale_findings(module: ParsedModule, thresholds: ModuleThresholds) -> list[Finding]:
# => confirmed boundary violation. Task 5 deletes it, Task 6 lands it in signals.
```

### Current shape of the code

```bash
wc -l src/humansays/analysis/*.py
#    13 __init__.py   237 body_visitor.py   145 models.py
#   342 python_ast.py 448 rules.py          151 syntax.py    1336 total

ls src/humansays/facts src/humansays/signals
#   ls: cannot access 'src/humansays/facts': No such file or directory
#   ls: cannot access 'src/humansays/signals': No such file or directory

# RulesetEvaluator has 17 methods, L53-411; three module-level helpers follow.
agentlens map src/humansays/analysis/rules.py
#   __init__ L54-70    run L72-85              _record L87-93
#   _evaluate_class L95-110                    _evaluate_function L112-135
#   _static_method L137-148                    _lambda_signals L150-162
#   _base_classes L164-174                     _argument_signals L176-200
#   _validated_bundle L202-224                 _size_signals L226-249
#   _control_flow_signals L251-277             _incident_signals L279-294
#   _state_signals L296-325                    _mutable_bindings L327-347
#   _class_state_surface L349-380              _class_cohesion L382-411
#   method_fields L414-415  cohesion_candidates L418-431  connected_components L434-448

# Six modules reference RulesetEvaluator; all must be updated in Task 7.
grep -rn 'RulesetEvaluator' src/ tests/
#   src/humansays/analysis/rules.py:53          src/humansays/analysis/__init__.py:5
#   src/humansays/application.py:17,99          tests/golden/test_parity.py:17,79
#   tests/integration/test_cli_contract.py:18,32  tests/unit/test_deleted_rules.py:9,20
#   tests/unit/test_rules.py:10,21              tests/unit/test_text_snapshot.py:17,58

# .migration/ is already gitignored — the baseline directory is safe to create.
grep -n 'migration' .gitignore
#   225:.migration/

# scripts/lint.sh subcommands:
sed -n '163,172p' scripts/lint.sh
#   format markdown ruff typecheck shell security deps imports deadcode   (default: all)

# PR template sections:
grep -n '^##' .github/PULL_REQUEST_TEMPLATE.md
#   1:## summary   5:## checklist   12:## Related Issues

# This plan's own location is outside docs_dir, so mkdocs --strict ignores it.
grep -n 'docs_dir\|site_dir' docs/mkdocs.yml
#   8:docs_dir: site        9:site_dir: ../site
```

### The trap: `cohesion_candidates` mutates its input

This is the single most dangerous thing in the refactor. It is not in the spec.

```bash
sed -n '418,431p' src/humansays/analysis/rules.py
```

```python
def cohesion_candidates(methods: list[FunctionFacts]) -> list[FunctionFacts]:
    names = {method.name for method in methods}
    for method in methods:
        non_fields = names | method.self_usage.methods_called
        method.self_usage.fields_read -= non_fields      # <-- MUTATES INPUT
        method.self_usage.fields_written -= non_fields   # <-- MUTATES INPUT

    return [
        method
        for method in methods
        if not method.trivial_accessor
        and method.name != '__init__'
        and method_fields(method)
    ]
```

`_evaluate_class` calls `_class_state_surface` **before** `_class_cohesion`
(`rules.py:109-110`), and `class_state_attributes` reads
`method.self_usage.fields_written`. So HS012/HS013 observe the *unstripped* sets
and HS008 observes the *stripped* ones. Reordering those two calls, or freezing
`FunctionFacts` for serializability, silently changes HS012/HS013 output.

Task 3 makes this function pure in an isolated commit, before any code moves.

### Pre-existing determinism risk — preserve, do not fix

```bash
sed -n '434,448p' src/humansays/analysis/rules.py
```

`connected_components` drives iteration with `remaining.pop()` on a `set[int]`.
For small ints `hash(i) == i`, so order is stable within an interpreter version,
and component order feeds HS008 evidence order. This already holds on `develop`.
Preserve it exactly. Fixing it would change output and belongs to a later phase.

### `FileReport.symbols` never reaches output

```bash
grep -rn 'symbols' src/humansays/reporting/ src/humansays/scoring.py
#   src/humansays/reporting/models.py:21:    symbols: set[str]
```

Its only consumer is `application.symbol_is_present` (`application.py:161-166`),
a membership test. It is never rendered, sorted, or counted. Ordering of this set
is therefore not an output-determinism concern.

---

## Scope Decisions

Three ambiguities in the spec were resolved with the operator before planning.

**1. Self-scan is carved out of invariant 1.** `test_self_scan.py` asserts exact
set equality between current weighted findings against `src/humansays` and the 6
entries in `self-scan-baseline.json`, keyed by `(path, symbol, line, rule_id,
evidence)`. Creating `facts/` and `signals/` under that root feeds new files to
the scanner, so byte-identical self-scan output is not achievable and claiming it
would be false. Invariant 1 is scoped to the poc-parity corpus and the Task 1 CLI
capture, both of which run over vendored third-party code this refactor does not
touch. Baseline churn is expected; every added or removed entry gets a
line-by-line justification in the PR. No current entry is in `analysis/`, so
nothing can go stale — the risk is *new* findings against the *new* modules.

**2. Phase B5 reduces to the boundary rule.** There is nothing to consolidate
(zero `version_info` matches). `requires-python` is `>=3.11`, but the `dev` and
`lint` dependency groups require `>=3.14` and every workflow pins 3.14. Adding
version-gated fixtures plus a 3.11–3.14 CI matrix is net-new feature work that
contradicts "structure only". Task 8 enforces the boundary and documents the
divergences; fixtures and the CI matrix defer to their own phase.

**3. `RulesetEvaluator` is deleted with no shim.** All six referencing modules are
rewritten in Task 7. The parity oracle (`poc.raw.json`, `django.raw.json`) is
unchanged, so it still proves output equivalence.

---

## File Structure

**Created**

| Path | Responsibility |
|---|---|
| `src/humansays/facts/__init__.py` | Re-exports the public fact types. No `ast`. |
| `src/humansays/facts/models.py` | `Signature`, `BodyFacts`, `SelfUsage`, `FunctionFacts`, `Scope`, `AnalysisIndex`, `MutationVocabulary`. |
| `src/humansays/facts/shape.py` | `ClassFacts`, `ModuleFacts`, `LambdaSite`, `MutableBinding`. |
| `src/humansays/analysis/extract.py` | `extract_module_facts(ParsedModule) -> ModuleFacts`. The only place `isinstance` dispatch on node type lives. |
| `src/humansays/signals/__init__.py` | `evaluate(ModuleFacts, Thresholds) -> list[Finding]`. |
| `src/humansays/signals/evaluator.py` | Ported rule bodies, fact-driven. |
| `src/humansays/signals/cohesion.py` | `method_fields`, `cohesion_candidates`, `connected_components`. Keeps `evaluator.py` under the 448-line bar. |
| `tests/unit/test_facts_purity.py` | Invariant 2, the version boundary, and the serialization round-trip. |
| `tests/unit/test_extract.py` | Single-walk assertion and fact-shape tests. |
| `tests/unit/test_signals.py` | Old-vs-new equivalence over the corpus. |

**Modified**

| Path | Change |
|---|---|
| `src/humansays/analysis/models.py:1-145` | Keeps only `ParsedModule`, `FunctionTarget`, `ScopeContext`, `FunctionNode`. |
| `src/humansays/analysis/python_ast.py` | Builds `ClassFacts`/`ModuleFacts`; loses `module_scale_findings`, `LambdaSite`, `MutableBinding`. |
| `src/humansays/analysis/rules.py` | Deleted entirely in Task 7. |
| `src/humansays/analysis/__init__.py:1-13` | Exports `parse_module`, `extract_module_facts`. |
| `src/humansays/application.py:97-116` | Orchestrates parse → extract → evaluate. |
| `.importlinter.ini` | Two new contracts, `layers` extended. |
| `tests/golden/self-scan-baseline.json` | Re-baselined in Task 9 with justification. |
| Five test modules referencing `RulesetEvaluator` | Rewritten onto the new entry points. |

**Layer order** in the `.importlinter.ini` `layers` contract becomes:
`application > scoring > reporting > signals > analysis > facts > catalog > config > findings`.
The layers contract permits `signals → analysis`; a separate `forbidden` contract
denies it (Task 6).

---

## Task 1: Baseline capture and branch

**Files:**
- Create: `.migration/phase-b-baseline/` (gitignored, `.gitignore:225`)
- Create: `.migration/capture.sh` (scratch; deleted in Task 9)

**Interfaces:**
- Consumes: nothing.
- Produces: `.migration/phase-b-baseline/` — the artifact every later task diffs against, and `.migration/capture.sh <output-dir>`, the command that regenerates it.

- [ ] **Step 1: Confirm the working tree and cut the branch**

The tree has `scripts/check_commit_msg.py` modified and one stash, both predating
this work. Confirm with the operator before proceeding if either is unexpected.

```bash
git status --short
git stash list
git switch develop && git pull --ff-only
git switch -c feat/phase-b-extraction-split
```

- [ ] **Step 2: Write the capture script**

Create `.migration/capture.sh`. Use `set -u` and `set -o pipefail` but **not**
`set -e` — the CLI exits nonzero by design when findings are present, and that is
the common case here.

```bash
#!/usr/bin/env bash
set -uo pipefail
out="${1:?usage: capture.sh <output-dir>}"
mkdir -p "$out"
for group in poc django; do
  root="tests/golden/poc-parity/corpus/${group}"
  [ -d "$root" ] || { echo "missing corpus: $root" >&2; exit 1; }
  for fmt in text json; do
    NO_COLOR=1 uv run humansays "$root" --format "$fmt" \
      > "${out}/${group}.${fmt}.nocolor" 2>&1
    FORCE_COLOR=1 uv run humansays "$root" --format "$fmt" \
      > "${out}/${group}.${fmt}.color" 2>&1
  done
done
cp tests/golden/self-scan-baseline.json "${out}/self-scan-baseline.json"
```

`NO_COLOR` and `FORCE_COLOR` are the exact variables the renderer reads
(`src/humansays/reporting/terminal.py:34-35`). `--format` accepts `text` and
`json` only (`src/humansays/enums.py:22-24`, `src/humansays/config/loading.py:173`).

- [ ] **Step 3: Prove the capture is reproducible**

A baseline that is not deterministic proves nothing. Capture twice, diff.

```bash
chmod +x .migration/capture.sh
.migration/capture.sh .migration/phase-b-baseline
.migration/capture.sh .migration/phase-b-recheck
diff -r .migration/phase-b-baseline .migration/phase-b-recheck && echo "REPRODUCIBLE"
rm -rf .migration/phase-b-recheck
```

Expected: `REPRODUCIBLE`. If the diff is non-empty, **stop and report** — there is
a pre-existing nondeterminism that must be understood before any refactor, because
every later verification step depends on this artifact.

- [ ] **Step 4: Record the green starting state**

```bash
uv run pytest
scripts/lint.sh
```

Expected: both pass. If either fails on a clean `develop`, stop and report.

- [ ] **Step 5: Commit**

`.migration/` is gitignored, so only the branch point is recorded here.

```bash
git commit --allow-empty -m "chore(phase-b): record branch point for extraction split"
```

---

## Task 2: The `facts` package

**Files:**
- Create: `src/humansays/facts/__init__.py`, `src/humansays/facts/models.py`
- Modify: `src/humansays/analysis/models.py:1-145`, `src/humansays/analysis/rules.py:70,96,120-126`
- Modify: `.importlinter.ini`
- Test: `tests/unit/test_facts_purity.py`

**Interfaces:**
- Consumes: `.migration/capture.sh` from Task 1.
- Produces: `humansays.facts.{Signature, BodyFacts, SelfUsage, FunctionFacts, Scope, AnalysisIndex, MutationVocabulary}`. `Scope` has fields `symbol: str, line: int, end_line: int` — **no `node`**. `analysis/models.py` retains `ParsedModule`, `FunctionTarget`, `ScopeContext`, `FunctionNode`.

- [ ] **Step 1: Write the failing purity test**

Create `tests/unit/test_facts_purity.py`. This test is the enforcer for the
"no `ast` in facts" claim at the module level; `import-linter` enforces it at the
package level in Step 5. Both are needed — one catches a stray runtime import, the
other catches a static one.

```python
import ast
import importlib
import pkgutil

import humansays.facts


def test_no_facts_module_exposes_ast() -> None:
    """No module in humansays.facts may hold a reference to the ast module."""
    for info in pkgutil.walk_packages(
        humansays.facts.__path__, prefix='humansays.facts.'
    ):
        module = importlib.import_module(info.name)
        offenders = [name for name, value in vars(module).items() if value is ast]
        assert not offenders, f'{info.name} exposes ast as {offenders}'


def test_scope_has_no_node_field() -> None:
    """Scope.node was dead weight and is the one thing blocking caching a Scope."""
    from humansays.facts import Scope

    assert 'node' not in Scope.__dataclass_fields__
```

- [ ] **Step 2: Run it to confirm it fails**

```bash
uv run pytest tests/unit/test_facts_purity.py -v
```

Expected: FAIL, `ModuleNotFoundError: No module named 'humansays.facts'`.

- [ ] **Step 3: Move the pure types**

Move `Signature` (L77-91), `BodyFacts` (L94-101), `SelfUsage` (L104-108),
`FunctionFacts` (L111-126), `AnalysisIndex` (L129-145), `MutationVocabulary`
(L61-64), and `Scope` (L47-58) from `analysis/models.py` into `facts/models.py`.
Verified during planning: none of these except `Scope` references `ast`.

`Scope` loses its `node` field. Its current body, with the one deletion marked:

```python
@dataclass(frozen=True, slots=True)
class Scope:
    node: ast.AST      # <-- delete this line
    symbol: str
    line: int
    end_line: int

    @property
    def span(self) -> int:
        return self.end_line - self.line

    def contains(self, line: int) -> bool:
        return self.line <= line <= self.end_line
```

`span` and `contains` are already line-based, so nothing else changes.

Carry `AnalysisIndex` across verbatim, including this behavior, which finding
order depends on — `min` returns the first element on a tie:

```python
def scope_for_line(self, line: int) -> Scope:
    candidates = [scope for scope in self.scopes if scope.contains(line)]
    if not candidates:
        return self.scopes[0]

    return min(candidates, key=attrgetter('span'))
```

Create `facts/__init__.py` re-exporting all seven names via `__all__`. Use
absolute imports throughout (`from humansays.facts.models import ...`).

`analysis/models.py` keeps `ParsedModule`, `FunctionTarget`, `ScopeContext`,
`FunctionNode` and imports what it needs from `humansays.facts`.

- [ ] **Step 4: Update the three `Scope(...)` construction sites**

All three are in `rules.py` and all pass a node as the first positional argument.

```python
# rules.py:70   was: self.index.add_scope(Scope(module.tree, '<module>', 1, span))
self.index.add_scope(Scope('<module>', 1, span))

# rules.py:96   was: self.index.add_scope(Scope(node, node.name, *node_span(node)))
self.index.add_scope(Scope(node.name, *node_span(node)))

# rules.py:120-126   was: Scope(node, qualified_name, facts.location.line, ...)
self.index.add_scope(
    Scope(qualified_name, facts.location.line, facts.location.end_line),
)
```

- [ ] **Step 5: Add the import-linter contract**

An unenforced boundary is not a boundary, so this lands in the same commit.
Append to `.importlinter.ini`:

```ini
[importlinter:contract:facts-has-no-parser]
name = humansays.facts must not import ast or tokenize
type = forbidden
source_modules =
    humansays.facts
forbidden_modules =
    ast
    tokenize
allow_indirect_imports = False
```

`allow_indirect_imports = False` is deliberate and stricter than the existing
`ast-confined-to-analysis` contract, which sets it to `True`. Facts must not reach
`ast` even transitively, or serializing them in Task 8 becomes impossible.

Also add `humansays.facts` to the bottom of the existing `layers` contract, below
`humansays.analysis`.

- [ ] **Step 6: Format, lint, test**

```bash
scripts/format.sh
scripts/lint.sh
uv run pytest
```

Expected: all pass. `scripts/lint.sh imports` must specifically report the new
`facts-has-no-parser` contract as kept.

- [ ] **Step 7: Verify output is unchanged**

```bash
.migration/capture.sh .migration/phase-b-check
diff -r .migration/phase-b-baseline .migration/phase-b-check \
  --exclude=self-scan-baseline.json && echo "OUTPUT UNCHANGED"
rm -rf .migration/phase-b-check
```

Expected: `OUTPUT UNCHANGED`.

- [ ] **Step 8: Commit**

```bash
git add src/humansays/facts src/humansays/analysis/models.py \
        src/humansays/analysis/rules.py .importlinter.ini \
        tests/unit/test_facts_purity.py
git commit -m "refactor(facts): split pure fact types out of analysis.models"
```

---

## Task 3: Make `cohesion_candidates` pure

Isolated deliberately. This is the one change in Phase B that can alter output
through a mechanism no reviewer will notice inside a large diff.

**Files:**
- Modify: `src/humansays/analysis/rules.py:382-411`, `:418-431`
- Test: `tests/unit/test_rules.py`

**Interfaces:**
- Consumes: `humansays.facts.FunctionFacts` from Task 2.
- Produces: `cohesion_candidates(methods: list[FunctionFacts]) -> tuple[list[FunctionFacts], list[set[str]]]` — the candidate methods and their stripped field sets, positionally aligned. Callers no longer read `method.self_usage` for cohesion. `method_fields(method: FunctionFacts) -> set[str]` and `connected_components(usage: list[set[str]]) -> list[list[int]]` keep their current signatures.

- [ ] **Step 1: Write the failing test that pins the ordering dependency**

Add to `tests/unit/test_rules.py`:

```python
def test_cohesion_candidates_does_not_mutate_input() -> None:
    """HS012 reads fields_written before HS008 runs; stripping in place changes HS012."""
    source = '''
class Widget:
    def alpha(self):
        self.left = 1
        return self.helper()

    def helper(self):
        return self.left

    def beta(self):
        self.right = 2
'''
    parsed = ParsedModule(Path('widget.py'), source, ast.parse(source))
    evaluator = RulesetEvaluator(parsed, Thresholds())
    evaluator.run()
    methods = evaluator.index.classes['Widget']
    written = {name for m in methods for name in m.self_usage.fields_written}
    assert written == {'left', 'right'}, (
        'fields_written was stripped in place by cohesion_candidates'
    )
```

- [ ] **Step 2: Run it to confirm it fails**

```bash
uv run pytest tests/unit/test_rules.py::test_cohesion_candidates_does_not_mutate_input -v
```

Expected: FAIL. `helper` is stripped out of the field sets because it is a method
name, demonstrating the in-place mutation.

- [ ] **Step 3: Make the function pure**

Replace `rules.py:418-431` entirely:

```python
def cohesion_candidates(
    methods: list[FunctionFacts],
) -> tuple[list[FunctionFacts], list[set[str]]]:
    """Methods worth judging for cohesion, with method names stripped from their fields.

    Returns the candidates and their field sets positionally aligned. The input
    facts are left untouched: HS012 reads ``self_usage.fields_written`` before
    HS008 runs, so stripping in place changes HS012's output.
    """
    names = {method.name for method in methods}
    candidates: list[FunctionFacts] = []
    usage: list[set[str]] = []
    for method in methods:
        non_fields = names | method.self_usage.methods_called
        fields = (
            method.self_usage.fields_read | method.self_usage.fields_written
        ) - non_fields
        if method.trivial_accessor or method.name == '__init__' or not fields:
            continue

        candidates.append(method)
        usage.append(fields)

    return candidates, usage
```

Iteration order over `methods` is preserved, so `candidates` and `usage` come out
in the same order the old two-pass version produced. That matters: `usage` index
order determines `connected_components` output, which determines HS008 evidence
order.

- [ ] **Step 4: Update the single caller**

`_class_cohesion` (`rules.py:382-411`) currently recomputes `usage` via
`method_fields`. Replace its first eight lines; the rest of the body is untouched:

```python
def _class_cohesion(self, node: ast.ClassDef, methods: list[FunctionFacts]) -> None:
    eligible, usage = cohesion_candidates(methods)
    fields = set().union(*usage) if usage else set()
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
```

`method_fields` is now unused by `_class_cohesion`. Leave it defined —
`scripts/lint.sh deadcode` (vulture) will say if it is fully orphaned, and Task 6
relocates it to `signals/cohesion.py`.

- [ ] **Step 5: Run tests and verify output**

```bash
uv run pytest
scripts/format.sh && scripts/lint.sh
.migration/capture.sh .migration/phase-b-check
diff -r .migration/phase-b-baseline .migration/phase-b-check \
  --exclude=self-scan-baseline.json && echo "OUTPUT UNCHANGED"
rm -rf .migration/phase-b-check
```

Expected: tests pass, `OUTPUT UNCHANGED`. If the diff is non-empty, the purity
change altered HS008 or HS012 — **stop and report** with the diff rather than
adjusting thresholds or the test.

- [ ] **Step 6: Commit**

```bash
git add src/humansays/analysis/rules.py tests/unit/test_rules.py
git commit -m "refactor(rules): make cohesion_candidates pure

It stripped method names from self_usage in place. HS012 reads
fields_written before HS008 runs, so the mutation was load-bearing
on call order and blocked freezing FunctionFacts."
```

---

## Task 4: `ClassFacts` and `ModuleFacts`

**Files:**
- Create: `src/humansays/facts/shape.py`
- Modify: `src/humansays/facts/__init__.py`, `src/humansays/facts/models.py`, `src/humansays/analysis/python_ast.py:53-68,110-127,307-342`
- Test: `tests/unit/test_extract.py`

**Interfaces:**
- Consumes: `humansays.facts.{FunctionFacts, Scope}` from Task 2.
- Produces: `humansays.facts.{ClassFacts, ModuleFacts, LambdaSite, MutableBinding}` with the exact fields below; `FunctionFacts.is_static: bool`; `build_class_facts(module: ParsedModule, node: ast.ClassDef, context: ScopeContext) -> ClassFacts`.

Every field traces to a consumer that exists today. Nothing speculative.

| `ClassFacts` field | Consumer verified in `rules.py` |
|---|---|
| `name: str` | HS012/HS013/HS008/HS018 via `location_of(node.name, node)` |
| `location: Location` | same |
| `bases: tuple[str, ...]` | `_base_classes` L164-174, HS018 |
| `declared_attributes: tuple[str, ...]` | `_class_state_surface` L349, via `declared_class_attributes` |
| `methods: tuple[FunctionFacts, ...]` | `_class_state_surface`, `_class_cohesion` |
| `mutable_bindings: tuple[MutableBinding, ...]` | `_mutable_bindings` L327, class scope, HS004 |

| `ModuleFacts` field | Consumer |
|---|---|
| `path: Path` | `application.analyze_file` |
| `line_count: int` | HS017, replacing `module_scale_findings` |
| `mutable_bindings: tuple[MutableBinding, ...]` | `run` L76, module scope, HS004 |
| `lambda_sites: tuple[LambdaSite, ...]` | `_lambda_signals` L150, HS016 |
| `functions: tuple[FunctionFacts, ...]` | top-level only; `AnalysisIndex.functions` |
| `classes: tuple[ClassFacts, ...]` | `AnalysisIndex.classes` |
| `scopes: tuple[Scope, ...]` | `AnalysisIndex.scope_for_line`, used by HS016 |
| `symbols: tuple[str, ...]` | `FileReport.symbols` |

- [ ] **Step 1: Write the failing shape test**

Create `tests/unit/test_extract.py`:

```python
from humansays.facts import ClassFacts, ModuleFacts


def test_class_facts_carries_what_the_class_rules_read() -> None:
    expected = {
        'name', 'location', 'bases', 'declared_attributes',
        'methods', 'mutable_bindings',
    }
    assert set(ClassFacts.__dataclass_fields__) == expected


def test_module_facts_carries_what_the_module_rules_read() -> None:
    expected = {
        'path', 'line_count', 'mutable_bindings', 'lambda_sites',
        'functions', 'classes', 'scopes', 'symbols',
    }
    assert set(ModuleFacts.__dataclass_fields__) == expected


def test_module_facts_holds_no_reference_to_another_file() -> None:
    """Per-file facts must be self-contained so they can be cached per file."""
    annotations = [
        str(field.type) for field in ModuleFacts.__dataclass_fields__.values()
    ]
    assert not [a for a in annotations if 'ModuleFacts' in a]
```

- [ ] **Step 2: Run it to confirm it fails**

```bash
uv run pytest tests/unit/test_extract.py -v
```

Expected: FAIL, `ImportError: cannot import name 'ClassFacts' from 'humansays.facts'`.

- [ ] **Step 3: Write `facts/shape.py`**

Move `LambdaSite` (`python_ast.py:53-58`) and `MutableBinding`
(`python_ast.py:61-68`) here unchanged — both are already pure:

```python
@dataclass(frozen=True, slots=True)
class LambdaSite:
    """A lambda expression and where it sits."""

    line: int
    source: str


@dataclass(frozen=True, slots=True)
class MutableBinding:
    """An assignment whose value is a mutable literal or container call."""

    name: str
    line: int
    end_line: int
    constructor: str


@dataclass(frozen=True, slots=True)
class ClassFacts:
    """What the class-level rules read, with no ast node behind it."""

    name: str
    location: Location
    bases: tuple[str, ...]
    declared_attributes: tuple[str, ...]
    methods: tuple[FunctionFacts, ...]
    mutable_bindings: tuple[MutableBinding, ...]


@dataclass(frozen=True, slots=True)
class ModuleFacts:
    """Everything the signals layer receives for one file.

    Self-contained by construction: no field references another file's facts,
    which is what makes per-file caching possible later. Cross-file correlation
    consumes many ModuleFacts at a higher layer. A future cache key must include
    the interpreter version — see the note in humansays/analysis/extract.py.
    """

    path: Path
    line_count: int
    mutable_bindings: tuple[MutableBinding, ...]
    lambda_sites: tuple[LambdaSite, ...]
    functions: tuple[FunctionFacts, ...]
    classes: tuple[ClassFacts, ...]
    scopes: tuple[Scope, ...]
    symbols: tuple[str, ...]
```

Tuples, not lists, throughout: these are the values that must be stable for
caching later.

- [ ] **Step 4: Order every set at the extraction boundary**

Invariant 1 depends on this. Sort at extraction, never at render time — `set`
iteration order is not stable across runs.

`declared_class_attributes` (`python_ast.py:110-127`) returns `set[str]`, so
`ClassFacts.declared_attributes` must be built as `tuple(sorted(...))`.
`AnalysisIndex.symbols` is a `set[str]`, so `ModuleFacts.symbols` must be
`tuple(sorted(...))`.

Two places are **already** correctly sorted and must not be double-sorted:
`_class_state_surface` emits `tuple(sorted(attributes))` for HS012 evidence, and
`attribute_prefix_clusters` emits `tuple(sorted(names))` under
`sorted(clusters.items())`. Leave both as they are.

- [ ] **Step 5: Add `is_static` to `FunctionFacts`**

`_static_method` (`rules.py:137-148`) reads `is_static_method(node)` and uses
`node.lineno` and `node.name` for evidence, plus `location_of(qualified_name, node)`.

Add `is_static: bool` to `FunctionFacts` in `facts/models.py`, populated in
`build_function_facts` (`python_ast.py:316-342`) from `is_static_method(target.node)`.

**Verify, do not assume:** HS015 evidence uses `node.lineno` directly, while
`location_of` goes through `node_span`, which reads `getattr(node, 'lineno', 1)`.
For a decorated function these must be the same line or HS015 output shifts.

```bash
uv run python -c "
import ast
t = ast.parse('@staticmethod\ndef f(): pass')
n = t.body[0]
print('lineno', n.lineno, 'decorator', n.decorator_list[0].lineno)
"
```

Expected: `lineno 2 decorator 1` — `lineno` points at `def`, not the decorator, so
`facts.location.line` is safe to use. If `lineno` is 1, **stop and report**: the
plan must add an explicit `def_line: int` field to `FunctionFacts` instead.

- [ ] **Step 6: Build the facts in `python_ast.py`**

Add `build_class_facts(module, node, context) -> ClassFacts` following the existing
`build_function_facts` pattern (`:316-342`). Do not wire it into `rules.py` yet —
Task 5 does the traversal move. `class_state_attributes` (`:307-313`) stays where
it is for now; Task 6 replaces its caller.

- [ ] **Step 7: Format, lint, test, verify output**

```bash
scripts/format.sh && scripts/lint.sh
uv run pytest
.migration/capture.sh .migration/phase-b-check
diff -r .migration/phase-b-baseline .migration/phase-b-check \
  --exclude=self-scan-baseline.json && echo "OUTPUT UNCHANGED"
rm -rf .migration/phase-b-check
```

- [ ] **Step 8: Commit**

```bash
git add src/humansays/facts src/humansays/analysis/python_ast.py \
        tests/unit/test_extract.py
git commit -m "feat(facts): add ClassFacts and ModuleFacts"
```

---

## Task 5: One traversal

**Files:**
- Create: `src/humansays/analysis/extract.py`
- Modify: `src/humansays/analysis/__init__.py:1-13`, `src/humansays/analysis/python_ast.py:249-263`, `src/humansays/analysis/rules.py:72-135`
- Test: `tests/unit/test_extract.py`

**Interfaces:**
- Consumes: `humansays.analysis.models.ParsedModule`, everything from Task 4.
- Produces: `humansays.analysis.extract_module_facts(module: ParsedModule, vocabulary: MutationVocabulary = MutationVocabulary()) -> ModuleFacts`. The only public extraction entry point. `module_scale_findings` is **deleted** from `python_ast.py`.

- [ ] **Step 1: Write the failing single-walk test**

Invariant 6 needs a test, not a convention. Add to `tests/unit/test_extract.py`:

```python
import ast
import collections
from pathlib import Path

from humansays.analysis import extract_module_facts
from humansays.analysis.models import ParsedModule


def test_extraction_walks_each_node_at_most_once(monkeypatch) -> None:
    """Invariant 6: per-rule walks are how this gets slow with nobody noticing."""
    path = Path('tests/golden/poc-parity/corpus/poc/rules.py')
    source = path.read_text(encoding='utf-8')
    parsed = ParsedModule(path, source, ast.parse(source))

    visits: collections.Counter = collections.Counter()
    real_walk = ast.walk

    def counting_walk(node):
        visits[id(node)] += 1
        return real_walk(node)

    monkeypatch.setattr(ast, 'walk', counting_walk)
    extract_module_facts(parsed)

    repeated = {key: count for key, count in visits.items() if count > 1}
    assert not repeated, f'{len(repeated)} nodes walked more than once'
```

- [ ] **Step 2: Run it to confirm it fails**

```bash
uv run pytest tests/unit/test_extract.py::test_extraction_walks_each_node_at_most_once -v
```

Expected: FAIL, `ImportError: cannot import name 'extract_module_facts'`.

- [ ] **Step 3: Write `extract.py`**

Move the traversal out of `RulesetEvaluator.run` (L72-85) and `_evaluate_class`
(L95-110). All `isinstance` dispatch on node type lives here and nowhere else.

The current traversal, for reference:

```python
def run(self) -> list[Finding]:
    self.findings.extend(module_scale_findings(self.module, self.thresholds.modules))
    self._mutable_bindings(self.module.tree.body, '<module>', 'module')
    for node in self.module.tree.body:
        if isinstance(node, FUNCTION_NODES):
            self._evaluate_function(node, node.name)

        elif isinstance(node, ast.ClassDef):
            self._evaluate_class(node)

    self._lambda_signals()
    return sorted(self.findings, key=attrgetter('sort_key'))
```

Preserve emission order exactly, because `run` sorts by `attrgetter('sort_key')`
and ties resolve by insertion order:

1. module-scope mutable bindings
2. each top-level node in `module.tree.body` order — function or class
3. within a class: class-scope bindings, then bases, then each method in
   `node.body` order
4. lambda sites last

Scope append order must also be preserved, because `AnalysisIndex.scope_for_line`
returns `min(candidates, key=attrgetter('span'))` and `min` returns the first
element on a tie. Module scope is appended first (`rules.py:70`), then each class,
then each function.

`_lambda_signals` calls `lambda_sites(self.module.tree)`, which is a full
`ast.walk` (`python_ast.py:274-279`). Folding it into the single traversal is
required by invariant 6 — collect lambda sites during the same walk rather than
calling `ast.walk` a second time. The test in Step 1 fails if you do not.

Add the caching and version note as the module docstring:

```python
"""Builds ModuleFacts from a parsed module in a single traversal.

A future per-file cache key must include the interpreter version. Facts extracted
under 3.12 are not valid under 3.14: ast.Str/ast.Num were removed, type_params was
added to FunctionDef/AsyncFunctionDef/ClassDef, ast.TypeAlias was added, PEP 701
changed JoinedStr structure and column offsets, and 3.13 added TypeVar defaults.
Normalizing those divergences is this module's job and nowhere else's. No caching
is implemented here.
"""
```

- [ ] **Step 4: Move `module_scale_findings` out**

Delete it from `python_ast.py:249-263`. Extraction produces `line_count`; the
threshold comparison and `Finding` construction move to signals in Task 6. Until
then, inline the HS017 emission at `rules.py:73-75` reading `facts.line_count`, so
output stays identical at this commit:

```python
count = facts.line_count
if count > self.thresholds.modules.max_lines:
    location = Location('<module>', 1, max(1, count))
    observation = Observation(
        f'Module spans {count} source lines.',
        (f'configured threshold: {self.thresholds.modules.max_lines}',),
    )
    self.findings.append(build_finding(SignalName.HS017, location, observation))
```

Wording is copied verbatim from the deleted function. Any change to the message
changes output.

- [ ] **Step 5: Export from the package**

`analysis/__init__.py` becomes:

```python
__all__ = ('RulesetEvaluator', 'extract_module_facts', 'parse_module')
```

`RulesetEvaluator` stays exported until Task 7 deletes it.

- [ ] **Step 6: Run everything**

```bash
scripts/format.sh && scripts/lint.sh
uv run pytest
.migration/capture.sh .migration/phase-b-check
diff -r .migration/phase-b-baseline .migration/phase-b-check \
  --exclude=self-scan-baseline.json && echo "OUTPUT UNCHANGED"
rm -rf .migration/phase-b-check
```

- [ ] **Step 7: Commit**

```bash
git add src/humansays/analysis tests/unit/test_extract.py
git commit -m "refactor(analysis): extract ModuleFacts in a single traversal"
```

---

## Task 6: The `signals` package

**Files:**
- Create: `src/humansays/signals/__init__.py`, `src/humansays/signals/evaluator.py`, `src/humansays/signals/cohesion.py`
- Modify: `.importlinter.ini`
- Test: `tests/unit/test_signals.py`

**Interfaces:**
- Consumes: `humansays.facts.ModuleFacts`, `humansays.config.models.Thresholds`, `extract_module_facts` from Task 5.
- Produces: `humansays.signals.evaluate(facts: ModuleFacts, thresholds: Thresholds) -> list[Finding]`, sorted by `attrgetter('sort_key')`. `humansays.signals.cohesion.{method_fields, cohesion_candidates, connected_components}`.

- [ ] **Step 1: Write the failing equivalence test**

The strongest test available: the new layer must produce exactly what the old one
does, on real code, before the old one is deleted. Create `tests/unit/test_signals.py`:

```python
from pathlib import Path

from humansays.analysis import extract_module_facts, parse_module
from humansays.analysis.rules import RulesetEvaluator
from humansays.config.models import Thresholds
from humansays.signals import evaluate


def test_signals_matches_the_evaluator_on_the_corpus() -> None:
    root = Path('tests/golden/poc-parity/corpus/poc')
    seen = 0
    for path in sorted(root.rglob('*.py')):
        parsed = parse_module(path)
        old = RulesetEvaluator(parsed, Thresholds()).run()
        new = evaluate(extract_module_facts(parsed), Thresholds())
        assert new == old, f'divergence in {path}'
        seen += 1

    assert seen > 0, 'corpus glob matched nothing; the test proved nothing'
```

The `seen > 0` assertion matters. A glob that silently matches nothing is a test
that passes while checking absolutely nothing.

- [ ] **Step 2: Run it to confirm it fails**

```bash
uv run pytest tests/unit/test_signals.py -v
```

Expected: FAIL, `ModuleNotFoundError: No module named 'humansays.signals'`.

- [ ] **Step 3: Port the rule bodies**

Move every `RulesetEvaluator` method into `signals/evaluator.py`, reading facts
instead of nodes. Do **not** split into per-rule-group modules — that is Phase C
and doing it now would be redone. The six AST-consuming sites become:

| Old | New |
|---|---|
| `_static_method(node, name)` reads `is_static_method(node)`, `node.lineno`, `node.name` | reads `method.is_static`, `method.location.line`, `method.name` |
| `_lambda_signals()` calls `lambda_sites(self.module.tree)` | iterates `facts.lambda_sites` |
| `_base_classes(node)` calls `base_class_names(node)` | reads `class_facts.bases` |
| `_mutable_bindings(body, ...)` calls `mutable_bindings(body, ...)` | reads `facts.mutable_bindings` / `class_facts.mutable_bindings` |
| `_class_state_surface(node, methods)` calls `class_state_attributes(node, methods)` | unions `class_facts.declared_attributes` with each `method.self_usage.fields_written` |
| `_class_cohesion(node, methods)` calls `location_of(node.name, node)` | reads `class_facts.location` |

HS017 moves here from the inlined form Task 5 left in `rules.py`:

```python
def _module_scale(facts: ModuleFacts, thresholds: ModuleThresholds) -> list[Finding]:
    if facts.line_count <= thresholds.max_lines:
        return []

    location = Location('<module>', 1, max(1, facts.line_count))
    observation = Observation(
        f'Module spans {facts.line_count} source lines.',
        (f'configured threshold: {thresholds.max_lines}',),
    )
    return [build_finding(SignalName.HS017, location, observation)]
```

Wording is verbatim from the original `module_scale_findings`. Any edit to the
message changes output.

`signals/cohesion.py` takes `method_fields` (`rules.py:414-415`),
`cohesion_candidates` (the pure version from Task 3), and `connected_components`
(`rules.py:434-448`). Keeping them in a separate module is what holds
`evaluator.py` under the 448-line bar checked in Task 9.

- [ ] **Step 4: Add the boundary contract**

Append to `.importlinter.ini`:

```ini
[importlinter:contract:signals-evaluates-over-facts]
name = humansays.signals must not import humansays.analysis, ast, or tokenize
type = forbidden
source_modules =
    humansays.signals
forbidden_modules =
    humansays.analysis
    ast
    tokenize
allow_indirect_imports = False
```

Insert `humansays.signals` into the `layers` contract above `humansays.analysis`.
The layers contract permits `signals → analysis`; this `forbidden` contract is what
actually denies it. Both are needed — the layers entry fixes the direction, the
forbidden entry closes the door.

- [ ] **Step 5: Run everything**

```bash
scripts/format.sh && scripts/lint.sh
uv run pytest
```

Expected: the equivalence test passes. If it fails, pytest's assertion diff names
the exact file and finding that diverged — fix the port, never the test.

- [ ] **Step 6: Commit**

```bash
git add src/humansays/signals .importlinter.ini tests/unit/test_signals.py
git commit -m "feat(signals): evaluate rules over ModuleFacts"
```

---

## Task 7: Delete `RulesetEvaluator`

**Files:**
- Delete: `src/humansays/analysis/rules.py`
- Modify: `src/humansays/analysis/__init__.py`, `src/humansays/application.py:97-116`
- Modify: `tests/golden/test_parity.py:16-17,79`, `tests/integration/test_cli_contract.py:18,32`, `tests/unit/test_deleted_rules.py:9,20`, `tests/unit/test_rules.py:10,21`, `tests/unit/test_text_snapshot.py:17,58`
- Delete from: `tests/unit/test_signals.py` (the `RulesetEvaluator` half of the equivalence test)

**Interfaces:**
- Consumes: `extract_module_facts` (Task 5), `evaluate` (Task 6).
- Produces: `application.analyze_file(path: Path, settings: ScannerSettings) -> FileReport`, signature unchanged; `FileReport` fields now sourced from `ModuleFacts`.

- [ ] **Step 1: Delete the god class and its module**

`rules.py` now contains only code that has been ported. Delete the file.
`analysis/__init__.py` becomes:

```python
__all__ = ('extract_module_facts', 'parse_module')
```

- [ ] **Step 2: Rewrite `analyze_file`**

Current body (`application.py:97-116`) reads `evaluator.index.classes`,
`.functions`, `.symbols`. Those move to `ModuleFacts`:

```python
def analyze_file(path: Path, settings: ScannerSettings) -> FileReport:
    parsed = parse_module(path)
    facts = extract_module_facts(parsed)
    findings = evaluate(facts, settings.thresholds)
    wanted = settings.selection.symbol
    if wanted:
        findings = [f for f in findings if matches_symbol(f.location.symbol, wanted)]
    return FileReport(
        path=path,
        lines=len(parsed.lines),
        classes=len(facts.classes),
        functions=len(facts.functions),
        symbols=set(facts.symbols),
        findings=findings,
    )
```

`FileReport.symbols` stays a `set[str]` — it is only membership-tested by
`symbol_is_present` (`application.py:161-166`) and never rendered, so changing its
type is out of scope.

**One semantic check is required here.** `evaluator.index.functions` was a flat
list that `_evaluate_function` appended to for *both* top-level functions and
methods (`rules.py:119`), while `facts.functions` as designed in Task 4 holds
top-level functions only. Confirm which count the old code produced:

```bash
grep -n 'index.functions' src/humansays/analysis/rules.py
```

If methods were counted, `analyze_file` must use:

```python
functions=len(facts.functions) + sum(len(c.methods) for c in facts.classes),
```

A wrong count changes the summary line in text output, and the Step 4 diff will
catch it — but knowing which way to fix it beforehand saves a cycle.

- [ ] **Step 3: Update the five test modules and trim the equivalence test**

Each of the five constructs `RulesetEvaluator(parsed, thresholds).run()`. Replace
with `evaluate(extract_module_facts(parsed), thresholds)`. `test_parity.py:16-17`
imports from both `humansays.analysis.models` and `humansays.analysis.rules`; the
second import moves to `humansays.signals`.

`tests/unit/test_signals.py` from Task 6 compares old against new. The old side no
longer exists — replace the body with a direct assertion that evaluation over the
corpus produces findings, keeping the `seen > 0` guard:

```python
def test_signals_produces_findings_over_the_corpus() -> None:
    root = Path('tests/golden/poc-parity/corpus/poc')
    seen = 0
    for path in sorted(root.rglob('*.py')):
        evaluate(extract_module_facts(parse_module(path)), Thresholds())
        seen += 1

    assert seen > 0, 'corpus glob matched nothing; the test proved nothing'
```

The real equivalence guarantee now comes from `tests/golden/test_parity.py`
against the unchanged `poc.raw.json` oracle.

- [ ] **Step 4: Run everything**

```bash
scripts/format.sh && scripts/lint.sh
uv run pytest
.migration/capture.sh .migration/phase-b-check
diff -r .migration/phase-b-baseline .migration/phase-b-check \
  --exclude=self-scan-baseline.json && echo "OUTPUT UNCHANGED"
rm -rf .migration/phase-b-check
```

`scripts/lint.sh deadcode` (vulture) will now flag anything the deletion orphaned.
Remove genuine orphans your own edit created; report pre-existing dead code rather
than deleting it.

- [ ] **Step 5: Commit**

```bash
git add -A src/humansays tests/
git commit -m "refactor: delete RulesetEvaluator in favour of extract-then-evaluate"
```

---

## Task 8: Version boundary and caching readiness

**Files:**
- Modify: `tests/unit/test_facts_purity.py`

**Interfaces:**
- Consumes: `extract_module_facts`, `parse_module`, `ModuleFacts`.
- Produces: no new public API. Three tests and one enforced boundary.

- [ ] **Step 1: Write the version-boundary test**

This is all that survives of spec step 25 after Scope Decision 2. `facts` and
`signals` must never learn which interpreter parsed the file. Add to
`tests/unit/test_facts_purity.py`:

```python
def test_facts_and_signals_never_branch_on_interpreter_version() -> None:
    """Normalization lives in humansays.analysis. Verified zero matches at plan time."""
    roots = [Path('src/humansays/facts'), Path('src/humansays/signals')]
    offenders = [
        f'{path}:{number}'
        for root in roots
        for path in sorted(root.rglob('*.py'))
        for number, line in enumerate(
            path.read_text(encoding='utf-8').splitlines(), 1
        )
        if 'version_info' in line
    ]
    assert not offenders, offenders
```

- [ ] **Step 2: Write the no-`ast`-reachable test**

Invariant 2. Recursive over dataclass fields, sequence elements and mapping
values — the spec is explicit that inspection is not the enforcer.

```python
import dataclasses
from collections.abc import Mapping


def _reachable(value, seen: set[int]):
    if id(value) in seen:
        return

    seen.add(id(value))
    yield value
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        for spec in dataclasses.fields(value):
            yield from _reachable(getattr(value, spec.name), seen)
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from _reachable(item, seen)
    elif isinstance(value, (list, tuple, set, frozenset)):
        for item in value:
            yield from _reachable(item, seen)


def test_no_ast_node_is_reachable_from_module_facts() -> None:
    path = Path('tests/golden/poc-parity/corpus/poc/rules.py')
    facts = extract_module_facts(parse_module(path))
    offenders = [
        value for value in _reachable(facts, set()) if isinstance(value, ast.AST)
    ]
    assert not offenders, f'{len(offenders)} ast nodes reachable from ModuleFacts'
```

- [ ] **Step 3: Write the serialization round-trip test**

The point is proving the fact model is data, not choosing a format. Stdlib only.

```python
import json


def test_module_facts_round_trips_through_json() -> None:
    path = Path('tests/golden/poc-parity/corpus/poc/rules.py')
    facts = extract_module_facts(parse_module(path))
    payload = dataclasses.asdict(facts)
    encoded = json.dumps(payload, default=str, sort_keys=True)
    decoded = json.loads(encoded)

    assert set(decoded) == set(payload), 'a top-level field vanished'
    assert decoded['line_count'] == facts.line_count
    assert len(decoded['classes']) == len(facts.classes)
    assert len(decoded['functions']) == len(facts.functions)
    assert len(decoded['scopes']) == len(facts.scopes)
    assert '<ast.' not in encoded, 'a node leaked through default=str'
```

Two things make this a real test rather than a tautology. The field and length
assertions compare the decoded payload against the *original object*, not against
a second encoding of itself. And the `'<ast.'` check matters because `default=str`
would happily stringify an AST node into `<ast.Module object at 0x7f...>`, letting
a round-trip pass while the fact model is still impure.

- [ ] **Step 4: Run the three tests**

```bash
uv run pytest tests/unit/test_facts_purity.py -v
```

Expected: all pass. If the reachability test fails, the offender list names what
still carries a node — fix extraction, not the test.

- [ ] **Step 5: Format, lint, commit**

```bash
scripts/format.sh && scripts/lint.sh && uv run pytest
git add tests/unit/test_facts_purity.py
git commit -m "test(facts): enforce ast-free, serializable, version-agnostic facts"
```

---

## Task 9: Verify and ship

**Files:**
- Modify: `tests/golden/self-scan-baseline.json`
- Delete: `.migration/`

**Interfaces:**
- Consumes: everything.
- Produces: a pull request.

- [ ] **Step 1: Full suite**

```bash
scripts/format.sh
scripts/lint.sh
uv run pytest
```

- [ ] **Step 2: Final baseline diff, with evidence**

```bash
.migration/capture.sh .migration/phase-b-final
diff -r .migration/phase-b-baseline .migration/phase-b-final \
  --exclude=self-scan-baseline.json
echo "exit=$?"
```

Expected: no output, `exit=0`. Paste the command and its output into the PR. Do not
assert cleanliness without showing it.

- [ ] **Step 3: Re-baseline the self-scan with per-entry justification**

```bash
uv run pytest tests/golden/test_self_scan.py -v
```

If it fails, the assertion message names each unexplained and stale entry. Update
`tests/golden/self-scan-baseline.json` and write one line per added or removed
entry in the PR, naming which new module triggered it and why the finding is
correct. A baseline entry added without a justification is a hidden regression.

- [ ] **Step 4: Confirm each contract by name**

```bash
scripts/lint.sh imports
```

Expected: five contracts kept — `acyclic-package`, `ast-confined-to-analysis`,
`facts-has-no-parser`, `signals-evaluates-over-facts`, and `layers`.

```bash
scripts/lint.sh deps
grep -n '^dependencies' pyproject.toml
#   27:dependencies = []
```

- [ ] **Step 5: Report the largest signals module**

```bash
wc -l src/humansays/signals/*.py | sort -rn
```

`analysis/rules.py` was 448 lines. If any single module in `signals/` exceeds that,
the god class moved rather than dissolved. **Report that rather than shipping it.**

- [ ] **Step 6: Clean up**

```bash
rm -rf .migration/
git status --short
```

Expected: clean. `.migration/` is gitignored, so nothing should appear.

- [ ] **Step 7: Open the PR**

Use `.github/PULL_REQUEST_TEMPLATE.md`, completing `## summary`, `## checklist`,
and `## Related Issues`. State each invariant next to the test that proves it, and
never write "enforced", "guaranteed", or "complete" without naming that test:

| Invariant | Enforcer |
|---|---|
| 1. Output unchanged (poc-parity + CLI capture) | `tests/golden/test_parity.py`; the Step 2 diff |
| 2. No `ast.AST` reachable from `ModuleFacts` | `test_no_ast_node_is_reachable_from_module_facts` |
| 3. `signals` imports neither `analysis` nor `ast`/`tokenize` | `import-linter` contract `signals-evaluates-over-facts` |
| 4. Zero runtime dependencies | `deptry` via `scripts/lint.sh deps` |
| 5. Exit codes unchanged | `tests/integration/test_exit_contract.py` |
| 6. One walk per module | `test_extraction_walks_each_node_at_most_once` |
| — `facts` has no parser import | contract `facts-has-no-parser`; `test_no_facts_module_exposes_ast` |
| — No version branch in `facts`/`signals` | `test_facts_and_signals_never_branch_on_interpreter_version` |
| — Facts are serializable data | `test_module_facts_round_trips_through_json` |
| — Self-scan drift | `tests/golden/test_self_scan.py`, re-baselined with per-entry justification |

The PR must also state plainly that **invariant 1 excludes `test_self_scan.py`**,
and why: that test scans `src/humansays` itself, so adding `facts/` and `signals/`
changes its input by construction. Invariant 5's enforcer is
`tests/integration/test_exit_contract.py`, not the `tests/cli/` path the spec
names — no such directory exists.

- [ ] **Step 8: Do not merge**

The operator owns git. Stop after opening the PR.

---

## Deferred

Recorded here so the next phase does not have to rediscover them.

- **Multi-interpreter fact extraction.** `requires-python = ">=3.11"` but CI pins
  3.14 everywhere. Needs version-gated fixtures and a 3.11–3.14 matrix covering
  `ast.Str`/`ast.Num` removal, `type_params`, `ast.TypeAlias`, PEP 701 `JoinedStr`
  spans (which affect `analysis/syntax.py` span reads), and 3.13 TypeVar defaults.
  A single-version test proves nothing about the range `requires-python` claims.
- **`connected_components` set-iteration order.** Deterministic in practice, not by
  construction. Fixing it changes HS008 evidence order, so it needs its own phase.
- **`ast-confined-to-analysis` enumerates `source_modules` by hand.** Every new
  module must be added manually or the contract silently stops covering it.
- **Phase C**: rule definition files, `RuleGroupDefinition`, the adapter protocol,
  per-group module layout.
