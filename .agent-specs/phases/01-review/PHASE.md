# Phase 1 — reconciliation review

**This phase reviews code that already exists.** The migration was implemented
from preliminary fragments before this documentation existed. The branch
(`feat/proof-of-concept`) is complete, CI is green, and a pull request is open.
Nothing here asks for a reimplementation.

**Goal.** Establish what was actually built, reconcile it against the
specifications that now exist, decide each divergence, and reserve the package
name before someone else does.

**Read this file only.** Later phase documents describe deferred work and will
generate change requests that do not belong in this review.

---

## Status and execution order

| Section                | Status                                              | Session                     |
| ---------------------- | --------------------------------------------------- | --------------------------- |
| **A** — inventory      | **complete** — `docs/evidence/phase-1-inventory.md` | done                        |
| **C** — tooling repair | pending                                             | next                        |
| **D** — prerelease     | pending                                             | next, same session as C     |
| **B** — reconciliation | pending                                             | fresh session after C and D |

**C and D run before B.** Both are mechanical and self-contained; reconciliation
is judgement work that benefits from the guard already being real, and from a
session that has not just spent an hour on packaging.

C and D share a session because they are both tooling. B gets a fresh one because
a session that just published a package is primed to conclude the package is
fine.

---

## Standing rule for this phase

> A divergence is not automatically a defect. The implementation predates the
> specification. Where they disagree, ask which is right before asking who
> should change.

Two divergences are already known — `HS002` on colour-toggle booleans and
`HS021` on optional-extra lazy imports. At least one traces to a known analyzer
defect rather than an implementation mistake. Expect more of that pattern.

---

## Section A — inventory (complete)

`docs/evidence/phase-1-inventory.md` records what is on disk. **Read it before
Sections B, C or D. Do not re-derive anything it already states.**

If a later section needs a fact the inventory does not contain, measure it and
append to the inventory rather than asserting it inline. The inventory is the
single record of ground truth for this phase.

---

## Section C — tooling repair

The scope guard shipped in an earlier documentation drop **did not work.**
Verified by test: it returned `scope ok` for a committed change to a supposedly
blocked file, for staged files outside every pattern, and for untracked files
outside every pattern. `git diff BASE...HEAD` sees only committed changes,
comments do not subtract from an earlier glob, and bash `[[ ]]` lets `*` cross
`/`, so `src/humansays/**` matched at any depth.

- [ ] Install `scripts/check_scope.py`
- [ ] Install `tests/tooling/test_scope_guard.py`
- [ ] Delete `scripts/check-scope.sh`
- [ ] Confirm every `allowed-paths.txt` carries its `!`-prefixed deny lines
- [ ] Wire the guard test into CI
- [ ] All eight cases in
      [`../../process/scope-guard.md`](../../process/scope-guard.md) pass

### The guard does not apply retroactively

`01-review/allowed-paths.txt` is review-shaped and would reject the migration
diff that this PR contains. **Do not run the guard against this PR's own diff,
and do not widen the allowlist to accommodate history.**

Scope enforcement applies from the review commits forward. Record this as a
stated exception in the reconciliation file.

Not optional cleanup. Every later phase depends on the guard, and until this
lands the strongest agent-safety claim in the documentation is false.

---

## Section D — prerelease and name reservation

**Goal.** Publish `0.1.0a1` to reserve the PyPI name and exercise the release
pipeline end to end.

### Why now rather than later

The name is unclaimed: `humansays` returns 404 on PyPI, while `pysignals` is
already taken by an unrelated project — which is why the rename happened. PyPI
effectively never releases a claimed name. Publishing an alpha costs an
afternoon; losing the name costs a rebrand.

The release workflow is also currently untested, and an alpha is the right thing
to test it against. `Development Status :: 3 - Alpha` is already declared.

### Rule IDs are not stable

Publishing makes the current `HS###` identifiers semi-public before Phase 2
renames them to `HS-<FAMILY>-NN`.

- [ ] README states, in one line, that rule IDs are unstable until `0.1.0`

That is the whole mitigation. Nobody pins an alpha.

### Tasks

1. **Version.** `0.1.0a1`, PEP 440 compliant. Add a test asserting
   `humansays --version` matches installed package metadata.
2. **Artifact smoke — per artifact, in a clean virtual environment.** For the
   wheel and the source distribution separately:
   install only that artifact → `humansays --version` → `humansays --help` →
   scan a fixture directory → validate the JSON → self-scan.

   This is the step that catches missing package data and accidental
   source-tree imports. Running it only against the working tree proves
   nothing.

3. **TestPyPI rehearsal.** Publish to TestPyPI, install from TestPyPI into a
   clean environment, re-run step 2 against the installed package.
4. **PyPI publish.**
5. **release.yml**. The workflow already exists — read it before planning. Adapt rather than replace: tag-triggered on v\*, verifies the tag matches the project version, builds once, runs the artifact smoke, then publishes. id-token: write scoped to the publish job only; contents: write scoped to the release job only. Record what changed and why.

### Known traps

**Trusted Publishing needs the project to exist.** The standard OIDC flow
requires an existing PyPI project. For a first upload you either configure a
_pending publisher_ on PyPI beforehand or use a scoped API token for `0.1.0a1`
and switch to Trusted Publishing afterwards. Check current PyPI documentation
rather than guessing — a failed first publish can leave a half-created project.

**Versions are immutable.** `0.1.0a1` can never be re-uploaded, even after
deletion. That is why steps 2 and 3 precede step 4.

**Entry point.** If the inventory shows `__init__.py` is empty as specified, the
console script must be `humansays.cli:main`, not `humansays:main`. A wrong entry
point installs cleanly and fails only on invocation — which step 2 catches.

_Configuration is the operator's job_. The agent cannot create PyPI accounts, configure pending publishers, or add repository secrets. It must stop and hand back a checklist at the point where those are needed, and never generate or echo a token.

### Acceptance

- [ ] Wheel and sdist each pass the full smoke sequence in a clean environment
- [ ] TestPyPI install passes the same sequence
- [ ] PyPI project page exists for `humansays`
- [ ] `release.yml` exists with the two permission scopes separated
- [ ] Version-metadata test passes
- [ ] mkdocs job remains disabled, not deleted

---

## Section B — reconcile against specification

Record **conforms**, **diverges**, or **not applicable** for each item, with a
disposition of `fix-now`, `defer-to-<phase>`, or `spec-wrong`.

Every row cites the inventory. If a row needs a fact the inventory lacks,
measure it and append there first.

### B1 — packaging and startup

| Expectation                                                                  | Why                                   |
| ---------------------------------------------------------------------------- | ------------------------------------- |
| `src/` layout, `uv_build` backend                                            | installed-artifact tests need it      |
| `__init__.py` contains only `__version__`                                    | measured: eager re-export cost 242 ms |
| `dependencies = []` literally true                                           | `deptry` should already enforce       |
| `rich` optional; ANSI fallback honors `NO_COLOR`, `FORCE_COLOR`, `TERM=dumb` |                                       |
| Import time under 40 ms                                                      |                                       |

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
- [ ] The **layers** contract declares `humansays.signals` even though that
      package does not exist yet. Phase 2 creates it, and the contract should
      predate the refactor it constrains. If the inventory shows only
      `acyclic`, `ast-confined-to-analysis` and `layers` without a `signals`
      layer, add it — this is a `fix-now`
- [ ] `analysis/rules.py` carries a docstring recording it as contract debt
- [ ] `ast.parse` lives in `analysis/`, and `SyntaxError` surfaces as a typed
      result rather than being swallowed

### B4 — the parity oracle

The highest-value artifact of the phase and the easiest to have gotten subtly
wrong. Parity **passing** is not the question; the question is what it proves.

- [ ] Fixtures store **raw** proof-of-concept output, with no ID rename applied
- [ ] The rename is applied by the harness from a reviewable mapping table
- [ ] From the inventory's `git log` evidence: were fixtures committed **before**
      the source they validate?
- [ ] Every entry in the parity diff traces to the mapping table or to one of
      the three deletions

**If fixtures were generated after the source, say so plainly.** The oracle is
then weaker than intended. That is recoverable — regenerate from
`.poc-reference/`, which is unchanged — but it must not be papered over by the
fact that the test passes.

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

#### `HS002` — verify before accepting the baseline reason

The existing baseline describes both entries as required-design false positives.
For `HS002` that is a conclusion, not an observation, and it may be wrong.

Read the parameter kinds from the inventory:

| Inventory says                                                               | Disposition                                                                                                                                                                                                |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| One or more flagged booleans are **positional** or **positional-or-keyword** | The tool is correct. Add `*,` to the signature. This satisfies the rule _and_ criteria §9 ("optional settings are keyword-only", "positional booleans are avoided") at zero cost. **Not debt — `fix-now`** |
| All flagged booleans are already **keyword-only**                            | The tool is wrong: this is the argument-kind defect. Baseline with reason citing Phase 2 Task 1, `expires: 02-fact-model`                                                                                  |

- [ ] The baseline reason for `HS002` reflects the observed parameter kinds

#### `HS021` — reduce, then baseline

Lazy import is genuinely correct for an optional extra, and `HS021` is already
slated for the opinionated profile. But N dispatch helpers each doing
`import rich` is N findings where one would do.

- [ ] Consolidate to a single lazy accessor, so the rule fires once
- [ ] Baseline the remainder with `expires` set to the phase that demotes
      `HS021`

### B6 — refactors made to satisfy the tool

Any structural change made **because the analyzer complained** gets scrutiny in
both directions. Use the inventory's record of call sites and shared state.

- [ ] Does each extracted unit have its own reason to change?
- [ ] Would you have made this split without the linter?
- [ ] Do the extracted pieces share most of their state, or are they only
      callable in sequence?

If the answer to the first two is no, or the third is yes, **revert the refactor
and baseline the original finding.** A tool that induces cosmetic refactoring in
its own source has demonstrated the defect it exists to detect. Carrying an
honest finding is better than carrying a worse implementation.

Specifically flagged: the `_render_rich` split, which moved the self-scan penalty
from 16.63 to 7.53. A penalty drop is not evidence the code improved.

### B7 — rule identifiers

The implementation uses `HS###` — a mechanical `PY` → `HS` prefix swap matching
the fragment it was built from. The specification now uses `HS-<FAMILY>-NN`.

**Disposition: defer to Phase 2.** Do not renumber in this PR. Phase 1's value is
the parity oracle; changing the mapping now means regenerating expectations for a
cosmetic reason, and the family rename is a mechanical pass that fits naturally
alongside the claim/certainty migration.

Section D publishes these identifiers as part of an alpha. That is acceptable
given the README caveat, and it does not change this disposition.

- [ ] Record where the current mapping table lives so Phase 2 can extend it

### B8 — public interface and small items

- [ ] **Exit codes.** The inventory records every code the CLI can return. The
      proof of concept used 1, 2 and 3. Any additional code — the inventory
      shows `--config /nonexistent` returning 4 — is a public interface
      addition and must appear in a documented exit-code table with a name. Fine
      if intentional; a defect if it fell out of an error path
- [ ] `type_comments=True` removed from `ast.parse`
- [ ] Tests pass on 3.11, 3.12, 3.13, 3.14
- [ ] `py.typed` shipped, `Typing :: Typed` classifier present
- [ ] Output is `path:line:col: ID message`, not a bordered table
- [ ] Summary exposes analysed / skipped / failed counts, or this is recorded as
      deferred
- [ ] Any test marked `skip` or `xfail` during CI repair has a recorded reason
      and a target phase

---

## Deliverables

1. `docs/evidence/phase-1-inventory.md` — **complete**
2. `docs/evidence/phase-1-reconciliation.md` — one row per specification item:
   conforms / diverges / not applicable, disposition, reason, inventory citation
3. `tests/golden/self-scan-baseline.json` — reviewed, with reasons and expiries
4. `scripts/check_scope.py` and `tests/tooling/test_scope_guard.py` — passing
5. `humansays 0.1.0a1` on PyPI, with `release.yml`
6. A PR description listing every deferred divergence and its target phase

---

## Merge policy

Merge on green CI plus a recorded reconciliation. Open issues for everything
deferred.

Holding a working branch open for a documentation-alignment pass costs more than
it buys. The reconciliation file and the PR description are the durable record;
the branch is not.

---

## Non-goals

- Reimplementing anything that works
- The argument-kind split (Phase 2 Task 1)
- The `HS-<FAMILY>-NN` rename (Phase 2)
- New rules, threshold changes, claim or certainty reassignment
- Splitting `analysis/rules.py` into extraction and evaluation (Phase 2)
- Correlation, findings, effects, dynamic analysis, scoring
- Re-enabling or repairing the mkdocs build
- Making the self-scan perfect

---

## What a wrong review looks like

1. **A reconciliation row asserts a fact the inventory does not contain.** If it
   was not measured, it is not evidence.
2. **A divergence was fixed without asking whether the specification was wrong.**
   At least one known case traces to an analyzer defect.
3. **The self-scan was made clean by weakening a rule or a threshold.** This is
   the failure mode the phase exists to prevent.
4. **`HS002` was baselined on the existing reason string** rather than on the
   observed parameter kinds. If any flagged boolean is positional, there is a
   real fix that costs nothing and the baseline entry is wrong.
5. **A refactor made to satisfy the tool was accepted because the penalty
   dropped.** A lower number is not evidence the code improved.
6. **Parity was accepted because the test passes.** The test passing says
   nothing about whether the oracle predates the code it validates.
7. **The scope guard was run against this PR's own diff**, and the allowlist was
   widened to make it pass. Enforcement starts from the review commits.
8. **`0.1.0a1` was published before the artifact smoke ran.** The version is
   immutable; a bad upload burns to `a2`.
9. **Deferred items were left out of the PR description.** They become invisible
   debt the moment the branch merges.
