# Extraction Enforcer Gaps Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the two enforcement gaps left by the extraction/evaluation split
(#19), without changing scanner output.

**Architecture:** Two tests and one honest specification note. Nothing in
`src/humansays` changes behaviour. The first test pins extraction's traversal
cost so a new full pass cannot land unnoticed. The second test makes the
hand-maintained `ast-confined-to-analysis` module list self-checking, so it
cannot silently stop covering a new module.

**Tech Stack:** Python 3.11+, stdlib only, `uv`, `pytest`, `ruff`, `ty`,
`import-linter`, `deptry`, `vulture`.

## Context

Phase B landed on `develop` as commit `41ceb74`, "refactor(analysis): split
RulesetEvaluator into extraction, facts, and signals (#19)". It went further
than the plan written for it: `signals/` is already split per rule group, which
that plan had deferred to Phase C. `RulesetEvaluator` and `analysis/rules.py`
are gone, `facts/` and `signals/` exist, and 196 tests pass at 96.55% coverage.

The plan at `docs/superpowers/plans/2026-07-29-phase-b-extraction-split.md` is
superseded and marked as such. Reviewing the merged result against that plan's
six invariants found four fully met, one met and better tested than planned, and
one unmet with no enforcer. This plan addresses what is left.

---

## Global Constraints

- **Zero runtime dependencies.** `dependencies = []` stays empty. `deptry` via
  `scripts/lint.sh deps` is the enforcer.
- **No `ast` or `tokenize` outside `humansays.analysis`.** Test code is exempt
  and already imports `ast` freely (`tests/unit/test_fact_model.py:10`).
- **Absolute imports inside `src/humansays`.** `TID252` via `.ruff.toml` is the
  enforcer; `scripts/format.sh` rewrites violations in place.
- **Scanner output must not change.** This plan adds tests only. No file under
  `src/humansays` is modified.
- **Run `scripts/format.sh` before `scripts/lint.sh`.** Never invoke
  `ruff`/`ty`/`deptry`/`lint-imports` directly. `scripts/format.sh` is the only
  quality script that writes to the repo.
- **Every enforcement claim names its enforcer.** If no test, hook, or CI job
  proves it, write it as convention. This plan exists because of that rule.
- **The operator owns git.** Commit as directed; do not push, merge, or branch
  without being asked.
- **Commit subject prefixes are restricted** to
  `feat|chore|ops|fix|release|docs`. The `commit-msg-format` pre-commit hook
  (`scripts/check_commit_msg.py`) is the enforcer, and it rejects `test`, so
  test-only commits go in under `chore`.
- **If a step cannot be completed as written, stop and report.**

---

## Facts Established During Planning

Every number below was measured on this tree at commit `41ceb74`. The scripts
that produced them are throwaway; the commands are given so the numbers can be
re-derived rather than trusted. Per project rule 11, none of these are
re-derived from reasoning — they are measurements.

### What the merged work already satisfies

| Planned invariant | Status | Enforcer |
|---|---|---|
| No `ast`/`tokenize` in `facts` | Met | `ast-confined-to-analysis` lists all 3 `facts` modules; `tests/integration/test_analysis_confinement.py` |
| `signals` imports neither `analysis` nor `ast` | Met | Same contract lists all 7 `signals` modules; `layers` writes `humansays.analysis \| humansays.signals` as co-equal siblings, banning both directions |
| No `ast.AST` reachable from facts | Met, tested better than planned | `tests/unit/test_fact_model.py::test_no_ast_node_is_reachable_from_module_facts`, plus `test_the_walk_would_find_a_node_if_one_were_there` guarding the walker itself |
| `Scope.node` dropped | Met | `src/humansays/facts/values.py:29-40` — fields are `symbol`, `line`, `end_line` |
| `cohesion_candidates` pure | Met | `src/humansays/signals/cohesion.py:17-26` returns `list[tuple[FunctionFacts, frozenset[str]]]`; no in-place mutation |
| Zero runtime dependencies | Met | `deptry` |

### Gap 1: extraction makes roughly 1.9 passes, and nothing checks it

Measured by patching `ast.iter_fields` — the one primitive both traversal paths
bottom out in, since `ast.iter_child_nodes` is implemented with it and
`ast.NodeVisitor.generic_visit` calls it directly.

```
tests/golden/poc-parity/corpus/poc/rules.py   1787 nodes   3405 reaches   1.91x
src/humansays/analysis/extraction.py           374 nodes    630 reaches   1.69x
src/humansays/signals/structure.py             311 nodes    562 reaches   1.81x
src/humansays/application.py                   671 nodes   1148 reaches   1.71x
```

Attributing each reach event to the nearest `humansays` frame:

```
  1786   52.5%  python_ast.py:descend        <- lambda_nodes, one complete extra pass
   685   20.1%  body_visitor.py:visit_Call
   306    9.0%  syntax.py:<genexpr>          <- referenced_names / contains_raise
   269    7.9%  body_visitor.py:visit_Attribute
   189    5.6%  body_visitor.py:visit_Assign
```

`python_ast.py:descend` is `lambda_nodes` (`python_ast.py:217-231`), reached
from `ModuleExtractor._lambdas` (`extraction.py:106-114`). Its 1786 reach events
over 1787 nodes is exactly one full extra traversal. The `syntax.py` share is
`referenced_names` and `contains_raise` doing small bounded subtree walks, not a
full pass.

**Three measurement traps, each of which produced a wrong answer first:**

1. Patching only `ast.iter_child_nodes` misses `FunctionVisitor` entirely, since
   `ast.NodeVisitor` uses `iter_fields`. That run reported 17% overhead instead
   of 91%. Patching both double-counts. Patch `iter_fields` alone.
2. `ast.Load`, `ast.Store`, `ast.Gt` and friends are interned singletons in
   CPython — one object stands in for every occurrence in the file. Counting by
   `id()` reported a single node "visited 1052 times". Exclude
   `ast.expr_context`, `ast.operator`, `ast.boolop`, `ast.unaryop`, `ast.cmpop`.
3. `id()` is only unique among live objects. Temporary ASTs built during
   extraction get their ids recycled and masquerade as repeat visits. Hold every
   real tree node alive in a dict and count only ids in that dict.

**The extra pass costs nothing measurable.** 40 interleaved trials, warmed up,
gc disabled, comparing shipped against `lambda_nodes` stubbed to return `[]`:

```
poc-parity corpus (17 files, 3111 lines)
  as shipped          : min 23.24 ms   median 27.04   stdev 2.12
  without lambda pass : min 23.17 ms   median 26.45   stdev 2.66
  difference of minima: +0.07 ms  (+0.3%)

src/humansays (42 files, 3335 lines)
  as shipped          : min 20.85 ms   median 25.70   stdev 1.99
  without lambda pass : min 21.33 ms   median 25.19   stdev 2.46
  difference of minima: -0.48 ms  (-2.3%)
```

Both differences sit inside a ~2 ms standard deviation, and they disagree in
sign. A first attempt without warmup or interleaving reported +10.6% and -11.8%
on the same two corpora — that was noise, and it is recorded here so nobody
re-derives it as a result. The honest conclusion is that the second pass has no
measurable cost: `lambda_nodes` descends via `iter_child_nodes`, which is cheap,
while the real time goes to `ast.unparse` and the visitor bodies.

**No shipped artefact claims a single walk.** The only "single traversal" text
in the tree is in the superseded plan. `extraction.py:1` says "The one place
that walks a module and turns it into facts", which is a claim about location,
not about pass count, and it is true.

```bash
grep -rn -e "single traversal" -e "walks the tree once" -e "second walk" docs .agent-specs src README.md
git log -1 --format=%B 41ceb74
#   refactor(analysis): split RulesetEvaluator into extraction, facts, and signals (#19)
```

So this is a missing enforcer against future regression, not a false claim to
retract.

**Scope decision, settled with the operator:** pin the cost with a test; do not
refactor. Eliminating the pass means folding lambda collection into
`FunctionVisitor` plus a shallow module- and class-level scan, then reproducing
`lambda_nodes`' global `(depth, position)` sort across two collectors. That sort
determines `ModuleFacts.lambdas` order and therefore HS016 finding order. Real
output risk, no measurable payoff. Recorded under **Deferred**.

### Gap 2: the contract's module list is hand-maintained

```bash
sed -n '15,52p' .importlinter.ini
```

`ast-confined-to-analysis` enumerates 33 `source_modules` by hand. A new module
added outside `humansays.analysis` is not covered until someone remembers to
add it, and `lint-imports` reports the contract as kept either way — it fails
open, silently.

This is **less severe than it first appears**:
`tests/integration/test_analysis_confinement.py:17-33` walks every `.py` under
`src/`, skips `analysis/`, and greps the parsed tree for `ast`/`tokenize`
imports. It derives its file set from the tree, so it covers new modules
automatically and is a genuine self-maintaining backstop.

The residual gap is the `.ini` list itself: nothing checks it is complete, so
`lint-imports` quietly weakens as the package grows while the test carries the
whole load alone.

### Verified starting state

```bash
git log --oneline -1        # 41ceb74
uv run pytest -q            # 196 passed, coverage 96.55% (required 85.0%)
```

---

## File Structure

**Created**

| Path | Responsibility |
|---|---|
| `tests/unit/test_extraction_cost.py` | Pins traversal reach-events-per-node below a ceiling, and proves the instrument would notice a new pass. |
| `tests/integration/test_import_contract_coverage.py` | Asserts `ast-confined-to-analysis` lists every non-`analysis` module in `src/humansays`. |

**Modified**

| Path | Change |
|---|---|
| `docs/superpowers/plans/2026-07-29-phase-b-extraction-split.md` | Superseded banner at the top. |
| `.agent-specs/backlog.md` | Two entries: the deferred single-pass refactor, and the measured traversal ratio. |

Nothing under `src/humansays` is modified.

---

## Task 1: Pin extraction's traversal cost

**Files:**
- Create: `tests/unit/test_extraction_cost.py`

**Interfaces:**
- Consumes: `humansays.analysis.extract`, `humansays.analysis.parse_module`.
- Produces: no importable API. A regression guard.

The metric is **reach events per distinct node**: how many times extraction
reaches each AST node, summed, divided by the number of nodes it reaches at
least once. Today that is 1.69–1.91 across representative files. The ceiling is
`2.5`: high enough to absorb interpreter drift in `ast.unparse` internals, low
enough that one new full pass (which would land near 2.9) fails the test.

This is a regression guard, not a precise budget. Do not tighten the ceiling to
hug the current number — a test that fails on a 3.15 upgrade for no behavioural
reason gets deleted rather than investigated.

- [ ] **Step 1: Write the failing test**

```python
"""Extraction's traversal cost, pinned so a new full pass cannot land unnoticed.

Measured, not asserted from reading: on this tree extraction reaches each node
1.69-1.91 times, because `lambda_nodes` descends the whole module a second time
after the main visitor pass. That second pass has no measurable wall-clock cost
(40 interleaved trials, difference inside one standard deviation), so it is
pinned here rather than removed. See the plan at
docs/superpowers/plans/2026-07-29-extraction-enforcer-gaps.md.
"""

from __future__ import annotations

import ast
import collections
from pathlib import Path

import pytest

from humansays.analysis import extract, parse_module

# Interned singletons: one ast.Load object stands in for every load context in
# the file, so counting it by identity is meaningless.
SINGLETONS = (ast.expr_context, ast.operator, ast.boolop, ast.unaryop, ast.cmpop)

MAX_REACHES_PER_NODE = 2.5

SAMPLES = (
    'src/humansays/analysis/extraction.py',
    'src/humansays/signals/structure.py',
    'src/humansays/application.py',
    'tests/golden/poc-parity/corpus/poc/rules.py',
)


def reaches_per_node(path: Path, monkeypatch: pytest.MonkeyPatch) -> float:
    """Mean number of times extraction reaches each node of `path`'s tree.

    Patches `ast.iter_fields` and nothing else: it is the one primitive both
    traversal paths bottom out in, since `ast.iter_child_nodes` is built on it
    and `ast.NodeVisitor.generic_visit` calls it directly. Patching
    `iter_child_nodes` instead would miss the function visitor, which is most of
    the work; patching both would double-count.
    """
    parsed = parse_module(path)
    # The dict keeps every node alive, so a recycled id() from a short-lived
    # temporary AST cannot be mistaken for a repeat visit.
    nodes = {
        id(node): node
        for node in ast.walk(parsed.tree)
        if not isinstance(node, SINGLETONS)
    }
    reaches: collections.Counter[int] = collections.Counter()
    real_iter_fields = ast.iter_fields

    def counting_iter_fields(node: ast.AST):
        for name, value in real_iter_fields(node):
            if isinstance(value, ast.AST):
                if id(value) in nodes:
                    reaches[id(value)] += 1
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST) and id(item) in nodes:
                        reaches[id(item)] += 1
            yield name, value

    monkeypatch.setattr(ast, 'iter_fields', counting_iter_fields)
    extract(parsed)
    monkeypatch.undo()

    assert reaches, f'the instrument recorded nothing for {path}'
    return sum(reaches.values()) / len(reaches)


@pytest.mark.parametrize('sample', SAMPLES)
def test_extraction_does_not_add_a_traversal(
    sample: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ratio = reaches_per_node(Path(sample), monkeypatch)
    assert ratio <= MAX_REACHES_PER_NODE, (
        f'{sample}: extraction now reaches each node {ratio:.2f} times, over the '
        f'{MAX_REACHES_PER_NODE} ceiling. Something added a pass over the tree.'
    )


def test_the_measurement_would_notice_an_added_traversal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A ceiling only means something if breaching it is detectable.

    Without this, an instrument that silently stopped counting would make every
    assertion above pass. Mirrors test_fact_model.py's
    test_the_walk_would_find_a_node_if_one_were_there.
    """
    from humansays.analysis import extraction

    real_extract = extraction.ModuleExtractor.extract

    def extract_with_a_spurious_walk(self):
        result = real_extract(self)
        for _ in ast.walk(self.module.tree):  # the regression being guarded against
            pass
        return result

    monkeypatch.setattr(
        extraction.ModuleExtractor, 'extract', extract_with_a_spurious_walk
    )
    ratio = reaches_per_node(Path('src/humansays/application.py'), monkeypatch)
    assert ratio > MAX_REACHES_PER_NODE, (
        f'an extra full walk only moved the ratio to {ratio:.2f}, which is under '
        f'the {MAX_REACHES_PER_NODE} ceiling -- the ceiling cannot catch a new pass'
    )
```

- [ ] **Step 2: Run it**

```bash
uv run pytest tests/unit/test_extraction_cost.py -v
```

Expected: five tests pass — four parametrized ceilings plus the
would-notice check.

If `test_the_measurement_would_notice_an_added_traversal` fails, the ceiling is
too loose to catch a real pass and must come down. If a parametrized case fails
on an unmodified tree, the measurement disagrees with the numbers recorded
above — **stop and report** rather than raising the ceiling to make it green.

**Resolved during implementation:** the helper restores `ast.iter_fields` with
`try`/`finally` rather than taking a `monkeypatch` fixture. Using `monkeypatch`
inside the helper would have made `undo()` also revert the `would_notice` test's
own patch of `ModuleExtractor.extract`, silently reducing that test to a
measurement of unmodified extraction. `try`/`finally` scopes the restore to the
one thing the helper patched, and the two mechanisms then compose without
ordering assumptions. The suite runs under `pytest-randomly`, so test order is
not fixed and any such coupling would be intermittent.

- [ ] **Step 3: Format, lint, full suite**

```bash
scripts/format.sh
scripts/lint.sh
uv run pytest
```

Expected: all pass, 201 tests.

- [ ] **Step 4: Commit**

```bash
git add tests/unit/test_extraction_cost.py
git commit -m "chore(analysis): pin extraction traversal cost

Extraction reaches each node 1.69-1.91 times: lambda_nodes descends the
whole module after the visitor pass. The second pass has no measurable
wall-clock cost, so it is pinned rather than removed. Nothing enforced
this before."
```

---

## Task 2: Make the ast contract's module list self-checking

**Files:**
- Create: `tests/integration/test_import_contract_coverage.py`

**Interfaces:**
- Consumes: `.importlinter.ini`, the `src/humansays` tree.
- Produces: no importable API. A completeness check.

`configparser` and `pathlib` are stdlib, so this adds no dependency.

- [ ] **Step 1: Confirm the shape of the list before coding against it**

```bash
uv run python -c "
import configparser
cfg = configparser.ConfigParser()
cfg.read('.importlinter.ini')
listed = cfg['importlinter:contract:ast-confined-to-analysis']['source_modules'].split()
print(len(listed), 'listed')
print('humansays' in listed, '<- is the root package listed?')
"
```

Record the answer. The assertion in Step 2 compares against every module in the
tree except `humansays.analysis*`; if the root package `humansays` is
deliberately absent, exclude it explicitly and say why in a comment rather than
adding it to the `.ini`.

- [ ] **Step 2: Write the failing test**

```python
"""The ast/tokenize contract enumerates its source modules by hand, so it fails
open: a new module outside humansays.analysis is simply not covered, and
lint-imports still reports the contract as kept.

tests/integration/test_analysis_confinement.py is the backstop that catches the
import itself. This test keeps the contract from quietly weakening underneath it.
"""

from __future__ import annotations

import configparser
from pathlib import Path

CONTRACT = 'importlinter:contract:ast-confined-to-analysis'


def module_name(path: Path, src_root: Path) -> str:
    relative = path.relative_to(src_root.parent)
    parts = relative.with_suffix('').parts
    if parts[-1] == '__init__':
        parts = parts[:-1]
    return '.'.join(parts)


def test_contract_covers_every_module_outside_analysis(src_root: Path) -> None:
    config = configparser.ConfigParser()
    config.read('.importlinter.ini')
    listed = set(config[CONTRACT]['source_modules'].split())

    expected = {
        module_name(path, src_root)
        for path in src_root.rglob('*.py')
        if path.relative_to(src_root).parts[0] != 'analysis'
    }
    # The root package humansays re-exports only; see Step 1's finding.
    expected.discard('humansays')

    missing = sorted(expected - listed)
    assert not missing, (
        f'{CONTRACT} does not list {missing}. The contract passes without '
        f'covering them, so add each to source_modules in .importlinter.ini.'
    )


def test_contract_lists_nothing_that_no_longer_exists(src_root: Path) -> None:
    """A stale entry is harmless to enforcement but hides that the list is unmaintained."""
    config = configparser.ConfigParser()
    config.read('.importlinter.ini')
    listed = set(config[CONTRACT]['source_modules'].split())

    real = {module_name(path, src_root) for path in src_root.rglob('*.py')}
    stale = sorted(listed - real)
    assert not stale, f'{CONTRACT} lists modules that do not exist: {stale}'
```

- [ ] **Step 3: Run it**

```bash
uv run pytest tests/integration/test_import_contract_coverage.py -v
```

Expected: both pass on the current tree, since the list was accurate when #19
landed. If `test_contract_covers_every_module_outside_analysis` fails now, the
list is *already* incomplete — add the named modules to `.importlinter.ini`,
then re-run `scripts/lint.sh imports` to confirm the contract still passes with
the wider source set. Report any module the wider set newly catches.

The `src_root` fixture already exists — `tests/integration/test_analysis_confinement.py:17`
takes it. Confirm its definition covers this directory:

```bash
grep -rn "def src_root" tests/
```

- [ ] **Step 4: Format, lint, full suite**

```bash
scripts/format.sh
scripts/lint.sh
uv run pytest
```

- [ ] **Step 5: Commit**

```bash
git add tests/integration/test_import_contract_coverage.py .importlinter.ini
git commit -m "chore(imports): check the ast contract lists every non-analysis module

The list is hand-maintained and fails open: an unlisted module is not
covered and lint-imports still reports the contract as kept."
```

---

## Task 3: Record what is deferred, and supersede the old plan

**Files:**
- Modify: `docs/superpowers/plans/2026-07-29-phase-b-extraction-split.md`
- Modify: `.agent-specs/backlog.md`

- [ ] **Step 1: Banner the superseded plan**

Insert directly under its `# ...` title:

```markdown
> **Superseded.** This work landed as commit `41ceb74`, "refactor(analysis):
> split RulesetEvaluator into extraction, facts, and signals (#19)", which went
> further than planned — `signals/` is already split per rule group. Kept for
> provenance. The gaps found reviewing the merged result are tracked in
> `2026-07-29-extraction-enforcer-gaps.md`.
```

- [ ] **Step 2: Add the backlog entries**

Read `.agent-specs/backlog.md` first and match its existing entry format rather
than imposing this one.

**The single-pass deferral is already recorded there**, as the entry beginning
"Folding `FunctionVisitor` into the single descent in `analysis/extraction.py`".
It names the blocker more precisely than this plan did: the risk is the append
order of `BodyFacts.incidents`, whose findings tie on `Finding.sort_key` and
depend on a stable sort, not only lambda ordering. Enrich that entry with the
measurements below; do not add a second one. Entries are sorted alphabetically
and the ordering carries no meaning, so place any new entry by its first word.

1. **Single-pass extraction** (update the existing entry).
   `lambda_nodes` (`python_ast.py:217-231`),
   reached from `ModuleExtractor._lambdas`, descends the whole module a second
   time — 52.5% of all node-reach events, exactly one extra full pass.
   Measured cost: none (differences of +0.3% and -2.3% across two corpora, both
   inside a ~2 ms standard deviation, 40 interleaved trials). Removing it means
   folding lambda collection into `FunctionVisitor` plus a shallow module- and
   class-level scan, then reproducing the global `(depth, position)` sort across
   two collectors. That sort sets `ModuleFacts.lambdas` order and therefore
   HS016 finding order, so it needs a full output baseline. Deferred for want of
   a payoff, not for want of feasibility.
2. **Traversal ratio is pinned at 2.5, not 1.9.**
   `tests/unit/test_extraction_cost.py` guards against a *new* pass, not against
   incremental creep. If the ratio is ever driven down deliberately, tighten the
   ceiling in the same change.

- [ ] **Step 3: Docs build, then commit**

`mkdocs.yml` lives at `docs/`, and the build is `--strict` with
`validation.omitted_files: warn`, so a new page under `docs/site/` without a
`nav:` entry fails. Neither file touched here is under `docs_dir` (`docs/site`),
so no nav entry is needed — but run the enforcer rather than assuming:

```bash
scripts/ci.sh docs
```

```bash
git add docs/superpowers/plans .agent-specs/backlog.md
git commit -m "docs(plans): supersede the phase B plan and record the deferred single-pass work"
```

---

## Task 4: Verify

- [ ] **Step 1: Full suite and lint**

```bash
scripts/format.sh
scripts/lint.sh
uv run pytest
```

- [ ] **Step 2: Confirm output did not change**

This plan adds no `src/` change, so the strongest available check is that
nothing under `src/` is in the diff:

```bash
git diff --stat develop...HEAD -- src/
echo "exit=$?"
```

Expected: empty output. If anything appears, a task modified `src/` and this
plan's central claim is void — **stop and report**.

- [ ] **Step 3: Confirm the contracts still pass by name**

```bash
scripts/lint.sh imports
```

Expected: three contracts kept — `acyclic-package`,
`ast-confined-to-analysis`, `layers`.

- [ ] **Step 4: Report, do not merge**

Summarize for the operator: the two new tests, the measured traversal ratio, and
the deferred refactor. The operator owns git beyond this branch.

---

## Execution Record: items carried over from the superseded plan

After Tasks 1–4 landed, the superseded Phase B plan was walked task by task
against the merged tree. Tasks 2–7 of that plan were fully delivered by #19.
Three items from its Tasks 8 and 9 were still outstanding and were executed
here.

- [x] **Output baseline (its Task 1).** `.migration/capture.sh` captures both
      corpora, both formats, colour forced on and off. Captured twice and
      diffed: reproducible. Re-checked after the only `src/` edit below:
      `OUTPUT UNCHANGED`. `.migration/` is gitignored (`.gitignore:225`) and was
      removed afterwards.
- [x] **Version-boundary test (its Task 8 Step 1).** Added to
      `tests/integration/test_analysis_confinement.py` rather than a new file,
      because that module is the established home for package-layout claims
      asserted against the real source tree. Verified by appending
      `sys.version_info` to `facts/values.py` and watching it fail with
      `facts/values.py:124`, then reverting.
- [x] **Caching-readiness note (its Task 8).** `analysis/extraction.py`'s
      docstring now records that a future cache key must include the
      interpreter version, and names the divergences that make it necessary.
      Docstring only; output re-verified unchanged.

One defect was found in the merged code while doing this and fixed in the same
commit. `test_fact_model.py::test_module_facts_round_trip_through_json`
asserted `restored == json.loads(json.dumps(payload, sort_keys=True))` —
a value against a second encoding of itself, which holds for any input
whatsoever. Two following assertions on `path` and `line_count` were carrying
the test alone. It now compares field names and collection lengths against the
original `ModuleFacts`.

Its Task 9 verification, run in full: self-scan passes with **no re-baselining
needed** (this work adds no module under `src/humansays`, so the concern in
Scope Decision 1 never materialized), parity passes, three contracts kept,
`dependencies = []`, and the largest `signals` module is `structure.py` at 110
lines against the 448-line bar `analysis/rules.py` set. Its Task 9 Step 7,
opening the PR, is left to the operator.

---

## Deferred

- **Single-pass extraction.** See Task 3 Step 2, entry 1.
- **`signals`/`analysis` independence has no direct test.** The `layers`
  contract's `humansays.analysis | humansays.signals` bans the import in both
  directions, and `lint-imports` is the enforcer. No pytest asserts it, unlike
  the `ast` ban which has `test_analysis_confinement.py` as a second enforcer.
  Symmetry would suggest one; not added here because `lint-imports` runs in
  `scripts/lint.sh` and in the CI `lint` job, so the boundary is enforced.
- **Multi-interpreter fact extraction.** The superseded plan claimed CI pins
  3.14 everywhere. **That was wrong**, and it is corrected here rather than
  carried forward: `ci-playbook.yml` runs a real `python-version` matrix, and
  PR #20 went green on 3.11, 3.12, 3.13 and 3.14. The backlog said as much all
  along. What remains open is narrower than the plan implied — the suite runs
  across the range, but there are no *fixtures using version-gated syntax*, so
  nothing exercises `ast.Str`/`ast.Num` removal, `type_params`, `ast.TypeAlias`,
  PEP 701 `JoinedStr` spans, or 3.13 TypeVar defaults. The matrix proves the
  existing tests pass everywhere; it does not prove the divergences are handled.
  A useful side effect: `tests/unit/test_extraction_cost.py`'s 2.5 ceiling is
  now known to hold on all four interpreters, which was the version-fragility
  concern that set it wide in the first place.
- **`connected_components` set-iteration order.** Deterministic in practice, not
  by construction. Carried over from the superseded plan; verify it still
  applies to `signals/cohesion.py` before acting on it.
