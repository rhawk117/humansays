# Phase 1 — reconciliation review

**This phase reviews code that already exists.** The migration was implemented
from preliminary fragments before this documentation existed. The branch
(`feat/proof-of-concept`) is complete and a pull request is open. Nothing here
asks for a reimplementation.

**Goal.** Establish what was actually built, reconcile it against the
specifications that now exist, and decide for each divergence: fix in this PR,
defer to a named phase, or accept that the specification is wrong.

**Read this file only.** Later phase documents describe deferred work and will
generate change requests that do not belong in this review.

---

## Standing rule for this phase

> A divergence is not automatically a defect. The implementation predates the
> specification. Where they disagree, ask which is right before asking who
> should change.

Two divergences already found — `HS002` on keyword-only booleans and `HS021` on
optional-extra lazy imports — trace to known analyzer defects, not to
implementation mistakes. Expect more of that pattern.

---

## Section A — inventory before judgement

Produce `docs/evidence/phase-1-inventory.md`. **Do not propose a single change
until it exists.** Reviewing against memory of what was supposed to happen is how
a review becomes a rewrite.

Record, from the code as merged:

- [ ] Package layout: is it `src/humansays/`? What does `__init__.py` contain?
- [ ] Build backend, console-script entry point, `requires-python`
- [ ] `dependencies` list, verbatim. Any optional extras and their guards
- [ ] Module map: every module, its imports, and whether it imports `ast` or
      `tokenize`
- [ ] Rule catalog: every ID, current name, and metadata fields
- [ ] Which rules were deleted, which renamed, which retained
- [ ] Test inventory: count, framework, directory structure, what each suite
      asserts
- [ ] Golden fixtures: do they exist, what do they contain, and — from
      `git log` — were they committed before or after the source they validate?
- [ ] Config discovery behavior, including the nonexistent-`--config` case
- [ ] Any `# TODO`, contract-debt docstring, or baseline file already present

Measure, do not assume:

```bash
python3 -X importtime -c "import humansays" 2>&1 | tail -1
python3 -m pytest -q
humansays --format json src/humansays | python3 -c "import json,sys; print(json.load(sys.stdin)['summary'])"
```

---

## Section B — reconcile against specification

Record **conforms**, **diverges**, or **not applicable** for each item, with a
disposition of `fix-now`, `defer-to-<phase>`, or `spec-wrong`.

### B1 — packaging and startup

| Expectation | Why |
|---|---|
| `src/` layout, `uv_build` backend | installed-artifact tests need it |
| `__init__.py` contains only `__version__` | measured: eager re-export cost 242 ms |
| `dependencies = []` literally true | `deptry` should already enforce |
| `rich` optional; ANSI fallback honors `NO_COLOR`, `FORCE_COLOR`, `TERM=dumb` | |
| Import time under 40 ms | |

If import time exceeds 40 ms, find out what is being imported before deciding
anything. The original 242 ms was one dependency, not diffuse cost.

### B2 — deletions

Phase 1 deletes `PY010` (comments), `PY011` (docstring), `PY020`
(future-annotations).

- [ ] All three absent from the rule **catalog**, not merely absent from output
- [ ] The `tokenize` pass backing `PY010` is gone
- [ ] A test asserts catalog absence

**Corrected measurement.** Deleting `PY010`+`PY011` is **22.5%** faster on
Django (4.18 s → 3.24 s, best of 3) and removes 60.8% of output volume with no
score change. `PY020` fires zero times on Django; it is deleted for correctness —
no identified compatibility or introspection hazard — not for speed.

An earlier draft claimed 26% and cited 3.22 s. Both were wrong: the 26% mixed two
measurement runs, and 3.22 s belongs to a set including `PY016`, which Phase 1
does not delete.

- [ ] Re-measure on this branch and record the actual delta. Do not copy the
      number above; verify it.

### B3 — parser containment

- [ ] Only `analysis/` imports `ast` or `tokenize`
- [ ] import-linter contracts exist and pass
- [ ] `analysis/rules.py` carries a docstring recording it as contract debt
- [ ] `ast.parse` lives in `analysis/`, and `SyntaxError` surfaces as a typed
      result rather than being swallowed

The layered contract should declare `humansays.signals` even though it does not
exist yet. If it does not, add it — Phase 2 creates that package, and the
contract should predate the refactor it constrains.

### B4 — the parity oracle

The highest-value artifact of the phase and the easiest to have gotten subtly
wrong.

- [ ] Fixtures store **raw** proof-of-concept output, with no ID rename applied
- [ ] The rename is applied by the harness from a reviewable mapping table
- [ ] `git log` shows fixtures committed before the source they validate
- [ ] Every entry in the parity diff traces to the mapping table or to one of
      the three deletions

**If fixtures were generated after the source, say so plainly.** The oracle is
then weaker than intended. That is recoverable — regenerate from
`.poc-reference/`, which is unchanged — but it must not be papered over.

### B5 — self-scan gate

The gate is **not** "weighted findings empty." That phrasing came from a
preliminary fragment and is stricter than this phase needs. Requiring a perfect
self-scan creates pressure to weaken rules, which is the failure mode most worth
avoiding in a tool that grades code.

The gate is:

- [ ] Zero parse errors
- [ ] All package files analysed
- [ ] Every remaining weighted finding appears in
      `tests/golden/self-scan-baseline.json` with a `reason` and an `expires`
      phase
- [ ] The check fails when a **new** finding appears, and also when a
      **baselined finding disappears** — the second catches stale entries nobody
      pruned
- [ ] Reasons live in the baseline file, not in docstrings. A docstring is
      invisible to CI and drifts silently

Expected entries:

| Finding | Disposition |
|---|---|
| `HS002` on colour-toggle booleans | **Check first whether the parameters are positional.** If so, make them keyword-only — that satisfies both the rule and criteria §9 at no cost, and is not debt. If they are already keyword-only, this is a false positive from the argument-kind defect; cite Phase 2 Task 1 and set `expires: 02-fact-model` |
| `HS021` on rich dispatch | Consolidate to a single lazy accessor so it fires once rather than N times, then baseline. `HS021` is slated for the opinionated profile |

### B6 — refactors made to satisfy the tool

Any structural change made **because the analyzer complained** gets scrutiny in
both directions.

- [ ] Does each extracted unit have its own reason to change?
- [ ] Would you have made this split without the linter?
- [ ] Do the extracted pieces share most of their state, or are they only
      callable in sequence?

If the answer to the first two is no, or the third is yes, **revert the refactor
and baseline the original finding.** A tool that induces cosmetic refactoring in
its own source has demonstrated the defect it exists to detect. Carrying an
honest finding is better than carrying a worse implementation.

Specifically flagged: the `_render_rich` split, which moved the self-scan penalty
from 16.63 to 7.53. Confirm it created real boundaries rather than a sequential
helper chain.

### B7 — rule identifiers

The implementation uses `HS###` — a mechanical `PY` → `HS` prefix swap matching
the fragment it was built from. The specification now uses `HS-<FAMILY>-NN`.

**Disposition: defer to Phase 2.** Do not renumber in this PR. Phase 1's value is
the parity oracle; changing the mapping now means regenerating expectations for a
cosmetic reason, and the family rename is a mechanical pass that fits naturally
alongside the claim/certainty migration.

- [ ] Record where the current mapping table lives so Phase 2 can extend it

### B8 — small items

- [ ] `type_comments=True` removed from `ast.parse`
- [ ] `--config` with a nonexistent path is an error
- [ ] Tests pass on 3.11, 3.12, 3.13, 3.14
- [ ] `py.typed` shipped, `Typing :: Typed` classifier present
- [ ] Output is `path:line:col: ID message`, not a bordered table
- [ ] Summary exposes analysed / skipped / failed counts, or this is recorded as
      deferred

---

## Section C — tooling repair

The scope guard shipped in an earlier documentation drop **did not work.**
Verified by test: it returned `scope ok` for a committed change to a supposedly
blocked file, for staged files outside every pattern, and for untracked files
outside every pattern. `git diff BASE...HEAD` sees only committed changes,
comments do not subtract from an earlier glob, and bash `[[ ]]` lets `*` cross
`/`, so `src/humansays/**` matched at any depth.

- [ ] Replace `scripts/check-scope.sh` with `scripts/check_scope.py`
- [ ] Add `!`-prefixed deny lines to every `allowed-paths.txt`
- [ ] Verify with the seven-case test in
      [`../../process/scope-guard.md`](../../process/scope-guard.md)

Not optional cleanup. Every later phase depends on the guard, and until this
lands the strongest agent-safety claim in the documentation is false.

---

## Deliverables

1. `docs/evidence/phase-1-inventory.md` — what exists, measured
2. `docs/evidence/phase-1-reconciliation.md` — one row per specification item:
   conforms / diverges / not applicable, with disposition and reason
3. `tests/golden/self-scan-baseline.json` — reviewed, with reasons and expiries
4. `scripts/check_scope.py` — working, with its test
5. A PR description listing every deferred divergence and its target phase

---

## Non-goals

- Reimplementing anything that works
- The argument-kind split (Phase 2 Task 1)
- The `HS-<FAMILY>-NN` rename (Phase 2)
- New rules, threshold changes, claim or certainty reassignment
- Splitting `analysis/rules.py` into extraction and evaluation (Phase 2)
- Correlation, findings, effects, dynamic analysis, scoring
- Making the self-scan perfect

---

## What a wrong review looks like

1. **Changes were proposed before the inventory existed.** The review became a
   rewrite driven by memory of intent rather than by what is on disk.
2. **A divergence was fixed without asking whether the specification was wrong.**
   Two known cases already trace to analyzer defects.
3. **The self-scan was made clean by weakening a rule or a threshold.** This is
   the failure mode the phase exists to prevent.
4. **`HS002` was baselined without checking whether the booleans are
   keyword-only.** If they are positional, there is a real fix that costs
   nothing.
5. **A refactor made to satisfy the tool was accepted without asking whether it
   improved the code.** Cosmetic refactoring is a finding, not a fix.
6. **Parity fixture ordering was not checked in `git log`.** An oracle generated
   after the code it validates proves nothing.
7. **Deferred items were left out of the PR description.** They become invisible
   debt the moment the branch merges.
