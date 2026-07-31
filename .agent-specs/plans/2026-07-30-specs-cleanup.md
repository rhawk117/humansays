# Specs Cleanup and Backlog Retirement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Delete `.agent-specs/backlog.md` and the retired per-phase machinery that still describes files which do not exist, do the small pieces of real work the backlog was holding, and leave every remaining specs document true against the tree.

**Architecture:** Three kinds of change, kept in separate tasks so a reviewer can reject one without rejecting its neighbours. First the code defects (three surveys that pass while examining nothing — a `CLAUDE.md` "Always 14" violation). Then the measured findings that live only in `backlog.md` get relocated into `docs/evidence/` before the file is deleted, because deleting them loses measurements that `CLAUDE.md` rule 11 says are re-run rather than re-derived. Then the documentation corrections, each one grep-verifiable afterwards.

**Tech Stack:** `uv` for every Python invocation. `pytest`. `scripts/format.sh`, `scripts/lint.sh`, `scripts/ci.sh docs`. No new dependency, no new module under `src/`.

---

## Decisions taken without an operator answer

Four decisions were put to the operator via `AskUserQuestion` and went
unanswered. The recommended option was taken in each case. Each is reversible;
if the operator disagrees, the named task is the one to change.

| Decision | Taken | Task | To reverse |
|---|---|---|---|
| The 38 LIVE backlog entries | Triaged. The verifiable ones become Tasks 1 and 4; the measured ones are relocated to `docs/evidence/` in Task 2; the rest are deleted with the file | 2, 6 | `git show` the deleted `backlog.md` |
| `plans/2026-07-26-docs-realignment.md` | Archived with a superseded banner, body untouched | 7 | Rewrite it fresh against the current layout |
| `review-checklist.md` step 1 | Step replaced. No new required section is imposed on future plans | 5 | Add the section to the plan template instead |
| Branch `chore/rules-relocation` | One PR, C1 and C2 halves separated in the description | 9 | Branch C2 off C1's tip |

A fifth question was decided without asking, because the obligation already
exists in the tree: `plans/2026-07-30-phase-c2-disposition-model.md:110` says
C2's exit-code consequence "must be in the changelog", and no changelog exists.
Task 3 creates `CHANGELOG.md`.

## Corrections to the audit this plan was written from

Two of the audit's findings did not survive checking. Do not act on them.

- **`plans/2026-07-29-phase-b-extraction-split.md` is not deleted.** The audit
  called it dead because it self-declares superseded. Its banner
  (lines 3–8) says "Kept for provenance; do not execute it" and names the
  commit that superseded it and the plan that inherited its gaps. That is
  exactly what an archived plan should look like. Deleting it destroys the
  provenance the file exists to carry. It is correct as it stands.
- **The audit's "not investigated: whether any CI workflow references the
  retired phase paths" is now answered: none does.** Verified 2026-07-30:

  ```bash
  grep -rn "phases/\|paths.json\|check_scope" .github/workflows/ scripts/
  ```

  returns only hits inside `scripts/check_scope.py` itself. No workflow, no
  hook, and no other script names any retired phase path. This is why Task 8
  can delete the script without touching CI.

## Global Constraints

Every task's requirements implicitly include this section.

- **`uv` only.** `uv run pytest`, `uv run python`. Never bare `python` or `pip`.
- **Never invoke `ruff`, `ty`, `vulture`, `deptry` or `lint-imports` directly.**
  Run `scripts/format.sh` first, then `scripts/lint.sh`. `format.sh` is the only
  quality script that writes to the tree.
- **Commit prefix is one of `feat|chore|ops|fix|release|docs`.** `test` is
  rejected by the `commit-msg` hook. Summary starts lowercase, no trailing
  period. Format: `prefix(scope): summary`.
- **Stage by explicit path. Never `git add -A`.** `scripts/check_commit_msg.py`
  carries a pre-existing one-blank-line modification that must not enter any
  commit in this plan.
- **`docs/evidence/` numbers are measured.** Task 2 relocates existing
  measurements verbatim. Do not re-derive, recompute, or round any number it
  moves.
- **`docs/evidence/` sits outside `docs_dir`** (`docs/mkdocs.yml` sets
  `docs_dir: site`, resolving to `docs/site`). A file added there needs no
  `nav:` entry. `CHANGELOG.md` at the repository root is likewise outside the
  build.
- **The operator owns git.** Commit the branch. **Do not push** — operator
  decision, 2026-07-30. Do not merge, rebase, reset, tag, or force anything.
  Task 9 prepares a PR body and reports the commit range; it does not push and
  does not open the PR.
- **Every enforcement claim names its enforcer** (`CLAUDE.md` rule 13). Prose
  this plan writes that says something is blocked, prevented or guaranteed must
  name the test, hook or CI job. Where none exists, write "convention".
- Verification commands, in this order, for any task that touches `tests/` or
  `src/`: `scripts/format.sh` → `uv run pytest` → `scripts/lint.sh`. For any
  task that touches `docs/site/`: `scripts/ci.sh docs`. Tasks touching only
  `.agent-specs/` need neither, and say so.

## Established facts

Verified by running the stated command on `chore/rules-relocation` on
2026-07-30. Do not re-derive; re-run the command if you doubt one.

- `find . -name paths.json -not -path './.git/*'` returns nothing. Every
  document describing a phase `paths.json` describes a file that does not exist.
- `ls .agent-specs/plans/` returns six files. Five are complete or superseded;
  `2026-07-26-docs-realignment.md` is the only one carrying no banner.
- `git tag --list` includes both `v0.1.0a1` and `v0.1.0a2`. `pyproject.toml:3`
  reads `version = "0.1.0a2"`. Twelve pages under `docs/site/` still say
  `0.1.0a1`. **Task 6 fixes only the two occurrences inside `.agent-specs/`.**
  The `docs/site/` drift is real but is a release-documentation question, not a
  specs-cleanup one; it is stated in Task 9's PR body as a known open item
  rather than silently fixed here.
- `tests/fixtures/sweeps.py` exists and exports `matching(directory, pattern)`
  and `python_sources(root, *packages)`. Both raise `AssertionError` rather than
  returning an empty list. Five test modules already route through it;
  `tests/unit/test_sweep_helpers.py` is where its own behaviour is asserted.
- `scripts/check_scope.py` has no caller. Its `ALLOWLIST_NAME = 'paths.json'`
  input does not exist anywhere in the tree, no hook or CI job invokes it, and
  `scope-guard.md` records that its test `tests/tooling/test_scope_guard.py`
  was removed.

## File structure

**Code (Task 1 only):**

| File | Change | Responsibility after |
|---|---|---|
| `tests/fixtures/sweeps.py` | add `entries()` | the single point where a sweep's corpus is enumerated, on disk or in a table |
| `tests/unit/test_sweep_helpers.py` | add two tests | asserts `entries()` refuses an empty table |
| `tests/golden/test_parity.py` | `_group_names()` routes through `entries()` | parity harness, no longer green against an empty manifest |
| `tests/unit/test_rule_registry.py` | `corpus_facts()` routes through `matching()` | registry coverage, no longer green against a missing corpus |
| `tests/unit/test_rule_messages.py` | `rendered_signals()` routes through `matching()` | template coverage, same |

**New files:**

| File | Responsibility |
|---|---|
| `CHANGELOG.md` | the user-visible record C2's plan requires; repository root, outside the docs build |
| `docs/evidence/backlog-measurements.md` | the measurements that lived only in `backlog.md`, relocated before it is deleted |

**Deleted files:**

| File | Why |
|---|---|
| `.agent-specs/process/scope-guard.md` | describes `paths.json` in phase directories that do not exist |
| `.agent-specs/backlog.md` | the operator has retired the concept |
| `scripts/check_scope.py` | Task 8, independently rejectable — no input, no caller, no test |

**Edited specs:** `process/agent-protocol.md`, `process/review-checklist.md`,
`design/00-overview.md`, `design/07-idea-register.md`, `README.md`,
`CLAUDE.md.template`, `plans/2026-07-26-docs-realignment.md`,
`plans/2026-07-30-phase-c1-rule-metadata-relocation.md`.

**Not touched, verified clean:** `design/01`–`06`, `roadmap-retirement.md`,
`plans/2026-07-27-test-suite-standardization.md`,
`plans/2026-07-29-extraction-enforcer-gaps.md`,
`plans/2026-07-29-phase-b-extraction-split.md`,
`plans/2026-07-30-phase-c2-disposition-model.md`.

---

## Task 1: Close the three surveys that pass while examining nothing

`CLAUDE.md` "Always 14" requires a uniqueness or coverage survey to assert that
its corpus reached every registration under test, and requires that assertion to
live in the shared helper the survey runs through. Three surveys bypass
`tests/fixtures/sweeps.py` and go green over an empty input.

`test_parity.py` is the worst of the three: `_group_names()` returns
`list(MANIFEST['groups'])`, and both `test_every_group_has_a_frozen_oracle` and
`test_humansays_matches_transformed_oracle_for_every_group` are `for` loops with
no assertion that the loop ran. If `manifest.toml` lost its `[groups]` table, or
if the key were renamed, the migration's whole acceptance criterion would pass
while comparing nothing.

`sweeps.py` has no helper for a table, only for a directory. This task adds one,
because "put the assertion in the helper" is the part of Always 14 that stops
the next author from writing the thin version again.

**Files:**
- Modify: `tests/fixtures/sweeps.py`
- Modify: `tests/unit/test_sweep_helpers.py`
- Modify: `tests/golden/test_parity.py:124-126`
- Modify: `tests/unit/test_rule_registry.py:89-99`
- Modify: `tests/unit/test_rule_messages.py:53-62`

**Interfaces:**
- Consumes: `matching(directory: Path, pattern: str) -> list[Path]` from
  `tests.fixtures.sweeps`, already present.
- Produces: `entries(mapping: Mapping[str, object], label: str) -> list[str]` in
  `tests.fixtures.sweeps`. Returns the mapping's keys sorted; raises
  `AssertionError` naming `label` when the mapping is empty. No later task
  depends on it.

- [ ] **Step 1: Write the failing tests for `entries()`**

Append to `tests/unit/test_sweep_helpers.py`:

```python
def test_entries_returns_sorted_keys() -> None:
    assert entries({'poc': 1, 'django': 2}, 'a table') == ['django', 'poc']


def test_entries_refuses_an_empty_table() -> None:
    with pytest.raises(AssertionError, match='manifest.toml'):
        entries({}, "manifest.toml's [groups]")
```

Add `entries` to the existing import at
`tests/unit/test_sweep_helpers.py:16`, so it reads:

```python
from tests.fixtures.sweeps import entries, matching, python_sources
```

That is the only import change needed. `pytest` is already imported at line 14
of that module, and `from __future__ import annotations` is already at line 10.

- [ ] **Step 2: Run them and confirm they fail for the stated reason**

```bash
uv run pytest tests/unit/test_sweep_helpers.py -v
```

Expected: both new tests fail at collection with
`ImportError: cannot import name 'entries' from 'tests.fixtures.sweeps'`. That
is the correct red — it is an import error only because the symbol does not
exist yet, which is what the test is for. If any *other* test in that file also
turns red, stop: the import edit broke something unrelated.

- [ ] **Step 3: Add `entries()` to the sweeps helper**

In `tests/fixtures/sweeps.py`, extend the `TYPE_CHECKING` block:

```python
if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path
```

Then add, after `matching()` and before `python_sources()`:

```python
def entries(mapping: Mapping[str, object], label: str) -> list[str]:
    """Every key of `mapping`, sorted, never empty.

    A manifest is a sweep whose corpus is enumerated in a file rather than
    found on disk, and it goes thin the same way `matching` does: a table that
    lost its rows leaves every loop over it green. `label` names the table, so
    the failure says which one went empty rather than only that something did.
    """
    found = sorted(mapping)
    if not found:
        raise AssertionError(
            f'{label} is empty, so the sweep about to run over it would '
            f'examine nothing and pass. Either the table lost its entries, or '
            f'the key that addresses it was renamed.'
        )

    return found
```

- [ ] **Step 4: Run the tests and confirm they pass**

```bash
uv run pytest tests/unit/test_sweep_helpers.py -v
```

Expected: PASS, all tests in the file.

- [ ] **Step 5: Route the parity manifest through it**

In `tests/golden/test_parity.py`, add to the import block (after the
`humansays` imports, matching the file's existing grouping):

```python
from tests.fixtures.sweeps import entries
```

Replace:

```python
def _group_names() -> list[str]:
    return list(MANIFEST['groups'])
```

with:

```python
def _group_names() -> list[str]:
    return entries(MANIFEST['groups'], "manifest.toml's [groups]")
```

The two callers loop over the result and assert per group, so the change from
insertion order to sorted order does not affect what they check.

- [ ] **Step 6: Route the two corpus sweeps through `matching()`**

In `tests/unit/test_rule_registry.py`, add to the import block:

```python
from tests.fixtures.sweeps import matching
```

and in `corpus_facts()`, replace:

```python
    for path in sorted(CORPUS.rglob('*.py')):
```

with:

```python
    for path in matching(CORPUS, '*.py'):
```

In `tests/unit/test_rule_messages.py`, add to the import block:

```python
from tests.fixtures.sweeps import matching
```

and in `rendered_signals()`, replace:

```python
    for path in sorted(CORPUS.rglob('*.py')):
```

with:

```python
    for path in matching(CORPUS, '*.py'):
```

- [ ] **Step 7: Prove the guard actually fires**

This is the step that distinguishes "the helper is called" from "the helper
would catch it". Break each input in turn and confirm the suite goes red, then
restore it.

```bash
git stash list  # note the count; there is one pre-existing stash
mv tests/golden/poc-parity/corpus tests/golden/poc-parity/corpus.bak
uv run pytest tests/unit/test_rule_registry.py tests/unit/test_rule_messages.py -x -q
```

Expected: FAIL with `AssertionError: ... contains no *.py, so the sweep about to
run over it would examine nothing and pass`. Before this task the same command
passed.

```bash
mv tests/golden/poc-parity/corpus.bak tests/golden/poc-parity/corpus
uv run pytest tests/golden/test_parity.py -x -q
```

Expected: PASS. Then confirm the manifest guard, without editing the committed
file:

```bash
uv run python -c "
import tests.golden.test_parity as p
p.MANIFEST = {'groups': {}}
try:
    p._group_names()
except AssertionError as exc:
    print('guard fired:', exc)
else:
    raise SystemExit('GUARD DID NOT FIRE')
"
```

Expected: `guard fired: manifest.toml's [groups] is empty, ...`

- [ ] **Step 8: Run the full gate**

```bash
scripts/format.sh
uv run pytest
scripts/lint.sh
```

Expected: 326 tests pass (324 before, plus the two added in Step 1). Coverage at
or above the 97.33% recorded on this branch. `scripts/lint.sh` exits zero,
including the three `lint-imports` contracts.

If `scripts/format.sh` rewrites anything beyond the five files this task names,
stop and report it — nothing else should be in scope.

- [ ] **Step 9: Commit**

```bash
git add tests/fixtures/sweeps.py tests/unit/test_sweep_helpers.py \
        tests/golden/test_parity.py tests/unit/test_rule_registry.py \
        tests/unit/test_rule_messages.py
git commit -m "chore(tests): route the last three sweeps through the empty-corpus guard"
```

---

## Task 2: Relocate the backlog's measurements before the file dies

`backlog.md` is deleted in Task 6. Four of its entries carry numbers that were
measured and exist nowhere else in the tree. `CLAUDE.md` rule 11 says measured
numbers are re-run rather than re-derived, and `agent-protocol.md` §9 says a
record is deleted only after its reasoning has been relocated. This task does
the relocation.

Everything else in `backlog.md` is an idea, an opinion, or a restatement of
something the code already says. Those go when the file goes.

**Files:**
- Create: `docs/evidence/backlog-measurements.md`

**Interfaces:**
- Consumes: nothing.
- Produces: nothing any later task imports. Task 6 requires this file to exist
  before it deletes `backlog.md`.

- [ ] **Step 1: Create the evidence file**

Write `docs/evidence/backlog-measurements.md` with exactly this content. Every
number is copied verbatim from `backlog.md`; none is recomputed.

```markdown
# Measurements recorded in the retired backlog

`.agent-specs/backlog.md` was deleted on 2026-07-30 when the project stopped
keeping a backlog. Four of its entries carried measurements rather than
intentions. Those are recorded here so the deletion loses no evidence, per
`CLAUDE.md` rule 11 and `agent-protocol.md` §9.

Nothing here is a plan. Each section states what was measured, when, and what
the measurement settled.

## Folding `FunctionVisitor` into the single descent — measured payoff is nil

Extraction runs one shallow visitor pass per function alongside the descent that
finds lambdas. Merging them was considered and measured rather than assumed.

- Extraction reaches each AST node **1.69–1.91 times**.
- `lambda_nodes` accounts for **52.5%** of all node-reach events — exactly one
  full extra pass.
- Stubbing it out changes wall-clock by **+0.3%** on the poc-parity corpus and
  **−2.3%** on `src/humansays`, both inside a **~2 ms** standard deviation over
  **40** interleaved trials. The two corpora disagree on the sign.

The merge would also perturb the append order of `BodyFacts.incidents`, which is
load-bearing: incidents of one signal in one function share a location, so their
findings tie on `Finding.sort_key` and the stable sort is what preserves their
order.

**Settled:** the payoff is nil, so the merge is not worth the behaviour risk.
`tests/unit/test_extraction_cost.py` pins the ratio instead, which is what keeps
a third pass from landing unnoticed.

## The traversal ceiling is deliberately loose

`tests/unit/test_extraction_cost.py` sets the ceiling at **2.5** reaches per node
against a measured **1.69–1.91**. The width absorbs drift in `ast.unparse`
internals across interpreter versions.

**Settled:** it catches a new full pass, which would land near **2.9**. It does
not catch incremental creep. If the ratio is ever driven down deliberately, the
ceiling has to be tightened in the same change or the gain is not held.

## Version normalization inside `humansays.analysis` is not warranted

Measured before deciding not to build it:

- **Zero** `sys.version_info` branches in `src/`.
- No reference to `ast.Str`, `ast.Num`, `type_params` or `ast.TypeAlias`.
- CI already runs the suite on **3.11 through 3.14**.

`tests/integration/test_analysis_confinement.py` fails if `version_info` appears
anywhere in `facts` or `rules`. `tests/unit/test_version_gated_syntax.py`
exercises PEP 695 type parameters, PEP 696 defaults, PEP 701 f-strings and
`ast.TypeAlias` under version gates across the same matrix. Extraction handled
all of them already.

**Settled:** a normalization boundary with no divergence to normalize and no
test that can fail is speculative. Revisit only if a fixture diverges.

## The byte-diff parity corpus is thin, and known to be

Measured July 2026:

- `poc` is **14** files and **0** signals, so four of its eight captured files
  are empty finding lists and comparing them proves nothing.
- `django` is **3** files and **9** findings, and is the whole of the evidence.

Phase C1 reported an empty byte diff at all **seven** commits on that basis.

The `poc` corpus is clean for a legitimate reason: it is the prototype's own
source, whose 20 self-findings were all comment and docstring counting, retired
as HS010 and HS011.

**Settled:** the corpus needs replacing rather than fixing, and a replacement
should fire every shipped rule at least once, asserted, so the gate cannot go
thin unnoticed. The capture script this measurement used (`.migration/capture.sh`)
no longer exists; `.migration/` was gitignored and has been deleted.
```

- [ ] **Step 2: Confirm the file is outside the docs build**

```bash
grep -n "docs_dir" docs/mkdocs.yml
scripts/ci.sh docs
```

Expected: `docs_dir: site`, and the build passes. `docs/evidence/` resolves
outside `docs/site/`, so the new page needs no `nav:` entry and `--strict` does
not see it. If the build fails, the file was written to the wrong directory.

- [ ] **Step 3: Commit**

```bash
git add docs/evidence/backlog-measurements.md
git commit -m "docs(evidence): relocate the backlog's four measurements before deleting it"
```

---

## Task 3: Create the changelog C2's plan requires

`plans/2026-07-30-phase-c2-disposition-model.md:110` states that C2's
consequence "is user-visible and must be in the changelog". The repository has
no changelog. `git tag --list` shows `v0.1.0a1` and `v0.1.0a2` both exist, and
`pyproject.toml:3` reads `0.1.0a2`, so the file starts with an Unreleased
section holding C1 and C2 and a released `0.1.0a2` line above `0.1.0a1`.

**Files:**
- Create: `CHANGELOG.md`

**Interfaces:**
- Consumes: nothing.
- Produces: nothing importable. Task 9's PR body links it.

- [ ] **Step 1: Write the changelog**

Create `CHANGELOG.md` at the repository root:

```markdown
# Changelog

Notable changes to `humansays`. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[PEP 440](https://peps.python.org/pep-0440/).

## Unreleased

### Added

- `--show-evidence` reveals findings from rules whose disposition is
  `evidence`, which are hidden by default.
- Rules carry a `disposition` of `on`, `hint`, `evidence` or `off`. `hint`
  findings are shown but contribute no penalty; `off` rules are not emitted at
  all.
- JSON output carries the rule's disposition.

### Changed

- **Scores move.** HS015, HS016 and HS021 are now `hint`, so they no longer
  contribute penalty. A file whose only findings are those three now scores as
  clean where it previously did not, and the process exit code changes with it.
  Nothing about detection changed; only what is weighed.
- Rule metadata (severity, confidence, weight, message templates) moved from
  Python literals into per-group `rules.toml` files under
  `src/humansays/rules/`. Output is byte-identical across this change.

### Removed

- `src/humansays/catalog.py` and the `signals/` package, replaced by
  `humansays.rules`. No rule was added or removed; all 19 `HS0NN` identifiers
  are unchanged.

## 0.1.0a2

Published to PyPI. See `docs/evidence/phase-1-cd-closeout.md` for the release
verification record.

## 0.1.0a1

First published alpha. 19 rules.
```

- [ ] **Step 2: Confirm it does not enter the docs build**

```bash
scripts/ci.sh docs
```

Expected: passes. `CHANGELOG.md` is at the repository root, outside
`docs/site/`, so `--strict` and `validation.omitted_files` do not see it. If the
build now fails complaining about an omitted file, the file was written into
`docs/site/` by mistake.

- [ ] **Step 3: Point the C2 plan at it**

In `.agent-specs/plans/2026-07-30-phase-c2-disposition-model.md`, find the
sentence at line 110 beginning "The consequence is user-visible and must be in
the changelog". Append to that paragraph:

```markdown
Recorded in `CHANGELOG.md` under Unreleased → Changed, 2026-07-30.
```

Do not rewrite the surrounding paragraph. This is a one-sentence addition that
closes the obligation by naming where it was met.

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md .agent-specs/plans/2026-07-30-phase-c2-disposition-model.md
git commit -m "docs(changelog): add the changelog C2 required and record the score change"
```

---

## Task 4: Retire the phase machinery from the agent protocol

`agent-protocol.md` §3 and §3a describe `paths.json` files in phase directories.
`find . -name paths.json -not -path './.git/*'` returns nothing. §1 tells a
session to execute tasks from exactly one `PHASE.md`; no `PHASE.md` exists.
§4c row 1 names `.migration/capture.sh`, deleted with `.migration/`. §6 sends
the reviewer to a "What a wrong implementation looks like" section that no plan
in this repository has ever contained.

§8 also contradicts the repository's own `CLAUDE.md`, which says "The operator
owns git. Do not commit, push, or branch unless asked." §8 says "Agents commit
and push their own branch." Project `CLAUDE.md` takes precedence, so §8 is the
side that changes.

`scope-guard.md` is deleted whole: roughly 40% of it describes the `paths.json`
format, and the rest describes a script Task 8 proposes deleting. The one idea
worth keeping — that a guard reading only the committed diff is trivially
bypassed — is preserved as a sentence in §3's replacement.

**Files:**
- Delete: `.agent-specs/process/scope-guard.md`
- Modify: `.agent-specs/process/agent-protocol.md` §1, §3, §3a, §4c, §6, §8, and
  the "What is actually enforced" table

**Interfaces:**
- Consumes: nothing.
- Produces: nothing. Task 5 edits `review-checklist.md`, which links here; the
  two tasks touch different files and can be reviewed independently.

- [ ] **Step 1: Delete the scope guard document**

```bash
git rm .agent-specs/process/scope-guard.md
```

- [ ] **Step 2: Rewrite §1**

Replace the whole of section 1 — from `## 1. One phase per session` through the
line ending `reliably produces scope drift.` — with:

```markdown
## 1. One plan per session

A session executes tasks from exactly one plan under [`plans/`](../plans/). Do
not read the other plans. They describe work that is either finished or
deliberately deferred, and reading them reliably produces scope drift.

A plan carrying a **Superseded** banner is provenance, not work. Do not execute
it, and do not treat its "Established facts" section as describing the current
tree.
```

- [ ] **Step 3: Replace §3 and delete §3a**

Replace everything from `## 3. Scope` through the end of §3a — that is, up to
but not including `## 4. Constraints that can be tests, are tests` — with:

```markdown
## 3. Scope

A plan states the files it touches. Changing anything outside that set is scope
drift, and the remedy is to stop and report the path and why it is needed, not
to widen the plan mid-execution.

**Nothing enforces this.** It was previously enforced by obligation against a
per-phase `paths.json` allowlist checked by `scripts/check_scope.py`. The phase
directories are gone and the allowlists with them, so the mechanism is gone
too; what remains is the reviewer reading the diffstat against the plan's file
list.

One lesson from that mechanism is worth keeping, because it applies to any
future check: `git diff BASE...HEAD` sees only committed changes, and a guard
reading it alone is bypassed by anything staged, unstaged, or untracked. A
scope check that does not read all four sources is not a scope check.
```

- [ ] **Step 4: Fix §4c row 1**

In the gate table under `## 4c. Every gate states what it is blind to`, replace
the first data row:

```markdown
| 1 | `.migration/capture.sh` + `diff -r` | CLI stdout over two corpora, both formats, colour both ways | anything the two corpora do not exercise; and whether the tests still test the same things | — |
```

with:

```markdown
| 1 | ~~`.migration/capture.sh` + `diff -r`~~ | CLI stdout over two corpora, both formats, colour both ways | anything the two corpora do not exercise; and whether the tests still test the same things | — |
```

and add immediately below the table, before the paragraph beginning "Ambient
and easy to overcount":

```markdown
Row 1 is struck because the script is gone: `.migration/` was gitignored and has
been deleted, so the byte-diff gate C1 relied on cannot be re-run. The row stays
in the table because the count of seven is the point being made, and dropping
the row would quietly restate it as six. What that gate covered is now covered
by nothing. The corpus it ran over was measured thin in any case — see
`docs/evidence/backlog-measurements.md`.
```

- [ ] **Step 5: Fix §6**

Replace the body of `## 6. Adversarial review before merge` — the paragraph
beginning "Every phase ends with" — with:

```markdown
Every plan ends with a review pass that assumes the implementation is wrong.
See [`review-checklist.md`](review-checklist.md). The reviewer starts from the
plan's verification commands and runs them, rather than reading the plan's
account of having run them.
```

- [ ] **Step 6: Reconcile §8 with `CLAUDE.md`**

Replace the first paragraph of `## 8. Git`:

```markdown
Agents commit and push their own branch. Agents do not merge, rewrite, or
destroy.
```

with:

```markdown
The operator owns git. `CLAUDE.md` rule 8 is the governing statement and this
section elaborates it rather than qualifying it: an agent commits, branches or
pushes **only when asked**, and never merges, rewrites, or destroys.

The permitted list below is what an agent may run *once asked*. It is not a
standing permission.
```

Leave the permitted, forbidden and `branch -D` paragraphs that follow unchanged.

Then, in the same section, replace:

```markdown
`push` is permitted so the operator can follow along. Force-push is not,
```

with:

```markdown
`push`, when asked, is permitted so the operator can follow along. Force-push is
not,
```

- [ ] **Step 7: Fix the "What is actually enforced" table**

Replace the two rows naming the retired machinery:

```markdown
| Scope stays inside `paths.json` | **nothing** -- §3, agent obligation |
| Allowlist derived from a search | **nothing** -- §3a, reviewer reads the commit body |
```

with a single row:

```markdown
| Scope stays inside the plan's file list | **nothing** -- §3, reviewer reads the diffstat |
```

And replace:

```markdown
| Drift folded downstream before close | **nothing** -- §9, reviewer checks at merge |
```

with:

```markdown
| Drift folded into the plan before close | **nothing** -- §9, reviewer checks at merge |
```

Then update the sentence below the table, which currently reads "The bottom five
rows are convention", to match the new row count:

```markdown
The bottom four rows are convention. They are listed so a reader knows which
lines the repository catches and which depend on the agent doing as told.
```

- [ ] **Step 8: Fix §9's phase vocabulary**

In `## 9. Phase close-out`, replace the heading and the numbered list's
downstream-document references. The heading becomes:

```markdown
## 9. Plan close-out
```

Replace the opening two lines:

```markdown
A phase is not complete when its acceptance criteria pass. It is complete
when every drift and defect entry it produced has been applied to the
downstream phase documents it affects.
```

with:

```markdown
A plan is not complete when its acceptance criteria pass. It is complete when
every drift and defect entry it produced has been written back into the plan
itself, under its **discovered-during-execution** section.

There is no downstream phase document to receive it. That was the old shape,
and it depended on a roadmap that no longer exists. The plan that produced the
finding is where the finding lives, because the next plan's author reads the
last plan and nothing else.
```

Then replace list items 2, 3 and 4:

```markdown
2. For each, identify the downstream phase document it changes.
3. Apply the change to that document, **relocating the reasoning, not only
   the conclusion.** A deferred decision that arrives downstream without the
   argument for deferring it will be re-litigated or silently reversed.
4. Commit as `ops(phase-N): fold drift into downstream phase docs`.
```

with:

```markdown
2. Write each into the plan's **discovered-during-execution** section,
   **recording the reasoning, not only the conclusion.** A deferred decision
   recorded without the argument for deferring it will be re-litigated or
   silently reversed.
3. If a measurement was taken, it goes to `docs/evidence/` instead, because
   plans are not re-run and measurements are.
4. Commit as `ops(<topic>): fold execution findings into the plan`.
```

Renumber the remaining item 5 to 4, keeping its text.

Finally, replace the closing paragraph:

```markdown
Evidence is per-phase and untracked -- working material, not an archive.
Anything that must outlive the phase belongs in a phase document before the
phase closes.
```

with:

```markdown
Working material is untracked and disposable. Anything that must outlive the
plan belongs in the plan, or in `docs/evidence/` if it is a number, before the
plan closes.
```

- [ ] **Step 9: Verify no retired machinery survives**

```bash
grep -rn "paths\.json\|PHASE\.md\|scope-guard\|\.migration/" .agent-specs/
```

Expected output: **only** the struck row and its explanatory paragraph in
`agent-protocol.md` §4c naming `.migration/capture.sh`, plus any hit inside
`plans/` — plans are historical records and are not rewritten. Specifically, no
hit in `process/`, `design/`, or `README.md` other than the §4c ones.

```bash
grep -rn "One phase per session\|phase document" .agent-specs/process/
```

Expected: no output.

This task touches no Python and no `docs/site/` page, so neither `uv run pytest`
nor `scripts/ci.sh docs` is required. Run them anyway if unsure; both should be
unaffected.

- [ ] **Step 10: Commit**

```bash
git add .agent-specs/process/agent-protocol.md
git rm --cached --ignore-unmatch .agent-specs/process/scope-guard.md
git commit -m "docs(specs): retire the phase and allowlist machinery from the protocol"
```

If `git rm` in Step 1 already staged the deletion, the `git rm --cached` line is
a no-op and can be skipped. Confirm with `git status --short` before committing
that exactly two paths are staged: the modified protocol and the deleted guard.

---

## Task 5: Make the review checklist satisfiable

Step 1 of `review-checklist.md` tells the reviewer to open the phase document's
"What a wrong implementation looks like" section. That phrase appears in no plan
in this repository and never has. A checklist whose first step cannot be
performed teaches the reviewer to skip steps.

Step 2 names `scripts/check-scope.sh`, which does not exist — the script was
`check_scope.py`, and Task 8 proposes deleting it. Step 2's other two boxes are
about `paths.json` and phase-document non-goals.

The replacement keeps the intent of step 1 — start from failure, not from
reading — but anchors it to something every plan actually has: verification
commands. `agent-protocol.md` §4c is the repository's own argument that a gate
list without blind spots produces a green run over a real defect, so that is
what the reviewer is sent to check.

**Files:**
- Modify: `.agent-specs/process/review-checklist.md:5-19`

**Interfaces:**
- Consumes: nothing. Task 4's §6 edit points here; the two are independent
  edits to different files.
- Produces: nothing.

- [ ] **Step 1: Replace step 1**

Replace:

```markdown
## 1. Failure modes first

Open the phase document's **"What a wrong implementation looks like"** section.
Attempt to confirm each listed failure before looking at anything else. These
are the specific mistakes predicted for this phase.
```

with:

```markdown
## 1. Run the gates before reading the diff

Open the plan's verification commands and **run them**. Do not read the plan's
account of having run them; a plan is written before execution and its
verification section records an intention.

Then, for each gate, write down what it cannot see. `agent-protocol.md` §4c is
the worked example: C1 listed five gates, ran seven counted by input, and two
pairs among the seven read the same thing. Two gates over one container are one
gate.

- [ ] Every verification command in the plan was run, by the reviewer, in this
      session
- [ ] Each gate has a stated blind spot
- [ ] No two gates in the list share an input without saying so
- [ ] Any gate that could not be run is reported as not run, never as passing
```

- [ ] **Step 2: Replace step 2**

Replace:

```markdown
## 2. Scope

- [ ] `scripts/check-scope.sh <phase>` passes
- [ ] If `paths.json` was widened, it happened in its own commit with a
      stated reason
- [ ] No change addresses a non-goal listed in the phase document
```

with:

```markdown
## 2. Scope

Nothing enforces scope. The diffstat against the plan's file list is the check.

- [ ] `git diff --stat <base>...HEAD` touches no file outside the plan's
      **Files** blocks
- [ ] Every file the plan named as touched actually changed, or the plan says
      why it did not
- [ ] No change addresses a non-goal the plan lists
```

- [ ] **Step 3: Fix the remaining phase vocabulary**

In section 3, under **Enforcement claims**, replace:

```markdown
- [ ] Every phase-document sentence claiming a mechanism prevents or guarantees
      something names the test that demonstrates it, and that test exists
```

with:

```markdown
- [ ] Every sentence in the plan or the docs it changes claiming a mechanism
      prevents or guarantees something names the test, hook or CI job that
      demonstrates it, and that enforcer exists
```

In section 8, replace:

```markdown
name the specific acceptance criterion that fails. "Feels wrong" is not a
verdict.
```

with:

```markdown
name the specific acceptance criterion that fails, and the command whose output
shows it failing. "Feels wrong" is not a verdict.
```

- [ ] **Step 4: Verify**

```bash
grep -rn "check-scope\|paths\.json\|phase document\|phase-document" .agent-specs/process/review-checklist.md
```

Expected: no output.

```bash
grep -c "^- \[ \]" .agent-specs/process/review-checklist.md
```

Expected: a count greater than before the edit — step 1 gained four boxes and
step 2 changed three for three. Record the number in the commit body.

- [ ] **Step 5: Commit**

```bash
git add .agent-specs/process/review-checklist.md
git commit -m "docs(specs): make review step 1 a command the reviewer can run"
```

---

## Task 6: Delete the backlog and correct the documents that describe it

The operator has retired the backlog outright. Task 2 has already relocated its
four measurements to `docs/evidence/backlog-measurements.md`; Task 1 has done
the code work it was holding. What remains in the file is ideas, which go with
it.

Three of its entries were also factually wrong and are worth naming so nobody
reconstructs them from the deleted file:

- "the vacant IDs in the `SignalName` enum, which suggest rules were dropped
  once already without a record" — false. HS010, HS011 and HS020 are documented
  in `docs/site/rules/index.md`.
- The confinement test was said to sweep `facts` or `signals`. It sweeps
  `DOWNSTREAM_PACKAGES = ('facts', 'rules')`, at
  `tests/integration/test_analysis_confinement.py:71`.
- `src/humansays/rules/loading.py` was said to be 195 lines. It is 205, and the
  entry's function list omits `_disposition`.

Two entries were resolved by this plan rather than deleted unread: the
`check_scope.py` review is settled by Task 8, and the git-ownership conflict
between `CLAUDE.md` and `agent-protocol.md` §8 is settled by Task 4.

`README.md` describes `backlog.md` in two places, omits two files from its
layout tree, and states the wrong version. `CLAUDE.md.template:85` states the
wrong version.

**Files:**
- Delete: `.agent-specs/backlog.md`
- Modify: `.agent-specs/README.md`
- Modify: `.agent-specs/CLAUDE.md.template:85`
- Modify: `CLAUDE.md:86` (repository root — carries the same stale version line)

**Interfaces:**
- Consumes: `docs/evidence/backlog-measurements.md` from Task 2. **This task
  must not run before Task 2 commits.**
- Produces: nothing.

- [ ] **Step 1: Confirm the measurements landed first**

```bash
test -f docs/evidence/backlog-measurements.md && echo OK || echo "STOP: run Task 2 first"
```

Expected: `OK`. If not, stop — deleting `backlog.md` now loses measurements
permanently, which is the failure `agent-protocol.md` §9 step 5 exists to
prevent.

- [ ] **Step 2: Delete the backlog**

```bash
git rm .agent-specs/backlog.md
```

- [ ] **Step 3: Rewrite the README's layout and version claims**

In `.agent-specs/README.md`, replace the layout block:

```markdown
```
.agent-specs/
├── process/     how agents work here; the review checklist
├── design/      reference documents for the evaluation model and architecture
├── backlog.md   unordered future work, deliberately not sequenced into phases
└── plans/       implementation plans, versioned with the code they change
```
```

with:

```markdown
```
.agent-specs/
├── process/              how agents work here; the review checklist
├── design/               reference documents for the evaluation model and architecture
├── plans/                implementation plans, versioned with the code they change
├── CLAUDE.md.template    the root CLAUDE.md's source; edit here, then copy
└── roadmap-retirement.md what the nine-phase roadmap was, and why it stopped
```
```

Replace the paragraph under `## On the retired phase roadmap`:

```markdown
This tree previously organized work into nine sequential phase
directories. That structure predated the shift to `NEW_RULES.md` as the
project's source of truth and has been retired: see
[`roadmap-retirement.md`](roadmap-retirement.md) for the phase-by-phase
disposition and [`backlog.md`](backlog.md) for the unordered work it left
behind. Only the next piece of work gets planned at a time; do not
reconstruct a phase sequence from the backlog.
```

with:

```markdown
This tree previously organized work into nine sequential phase directories,
then into an unordered `backlog.md`. Both are retired. See
[`roadmap-retirement.md`](roadmap-retirement.md) for the phase-by-phase
disposition.

**There is no backlog.** Work that is worth doing is planned and done; work
that is not is not written down. A list of things nobody is doing accrues
claims that stop being true, and this repository has now had that happen twice.
The measurements the backlog held were moved to
`docs/evidence/backlog-measurements.md` before it was deleted.

Only the next piece of work gets planned at a time.
```

Replace the version sentence in the opening section:

```markdown
The documentation site is the source of truth for both rule sets. The 19 rules
that ship in `0.1.0a1` are under Rules, one page per group, each carrying the
```

with:

```markdown
The documentation site is the source of truth for both rule sets. The 19 rules
that ship in `0.1.0a2` are under Rules, one page per group, each carrying the
```

Finally, replace the stale protocol reference in the first paragraph:

```markdown
[`plans/`](plans/) and are reviewed against the protocol's §4 constraint table
before they are executed, not after. Standing constraints live
```

with:

```markdown
[`plans/`](plans/) and are reviewed against the protocol's §4 constraint table
before they are executed, not after. There is no backlog: see below. Standing
constraints live
```

- [ ] **Step 4: Fix the template's version**

In `.agent-specs/CLAUDE.md.template`, line 85, replace:

```markdown
  `0.1.0a1` ships 19. Never document a planned rule as shipped.
```

with:

```markdown
  `0.1.0a2` ships 19. Never document a planned rule as shipped.
```

The root `CLAUDE.md` carries the same line and needs the same change. Verified
2026-07-30: `grep -n "0\.1\.0a1" CLAUDE.md` returns

```
86:  `0.1.0a1` ships 19. Never document a planned rule as shipped.
```

Apply the identical edit at `CLAUDE.md:86`, so the line reads:

```markdown
  `0.1.0a2` ships 19. Never document a planned rule as shipped.
```

The template and the root file are meant to agree; committing one without the
other reintroduces the drift this step exists to close.

- [ ] **Step 5: Verify nothing still points at the deleted file**

```bash
grep -rn "backlog" .agent-specs/ CLAUDE.md docs/site/ 2>/dev/null
```

Expected: hits only in `.agent-specs/README.md` (the "There is no backlog"
paragraph), `.agent-specs/roadmap-retirement.md`, and inside `plans/` — plans
are historical and are not rewritten. **No hit in `process/` or `design/`.**

If `roadmap-retirement.md` links `backlog.md` as a live destination, change that
link's text to name `docs/evidence/backlog-measurements.md` instead. Report the
edit; the audit graded that file clean, so this would be a finding the audit
missed rather than a planned change.

```bash
grep -rn "0\.1\.0a1" .agent-specs/
```

Expected: hits only in `roadmap-retirement.md:31` (a statement about what
shipped, historically true) and inside `plans/`. No hit in `README.md` or
`CLAUDE.md.template`.

- [ ] **Step 6: Commit**

```bash
git add .agent-specs/README.md .agent-specs/CLAUDE.md.template CLAUDE.md
git commit -m "docs(specs): delete the backlog and correct the documents that described it"
```

`CLAUDE.md` is in the list because Step 4 changes it — the two version lines
land in one commit or the drift survives. Step 2's `git rm` already staged the
deletion of `.agent-specs/backlog.md`; confirm with `git status --short` that
`D  .agent-specs/backlog.md` is present before committing, and that
`scripts/check_commit_msg.py` is **not**.

---

## Task 7: Banner the two plans that describe a tree that no longer exists

`plans/2026-07-26-docs-realignment.md` is 1000 lines and carries no banner. Its
goal names `NEW_RULES.md`, which is untracked and deleted, and it carries six
references to `catalog.py` and `signals/`, both removed in C1. Its actual
outcomes — the per-domain planned catalog under `docs/site/planned/`, the
roadmap retirement — have landed. It is finished, not open.

`plans/2026-07-30-phase-c1-rule-metadata-relocation.md` executed successfully,
but its "Context" and "Established Facts" sections describe `catalog.py` and
`signals/` in the present tense, as things a reader will find. A future agent
opening it to learn the tree learns a tree that was deleted by the plan itself.

Neither is rewritten. A banner is enough, and rewriting an executed plan's facts
section destroys the record of what the author actually believed.

**Files:**
- Modify: `.agent-specs/plans/2026-07-26-docs-realignment.md:1-5`
- Modify: `.agent-specs/plans/2026-07-30-phase-c1-rule-metadata-relocation.md:1-3`

**Interfaces:**
- Consumes: nothing.
- Produces: nothing.

- [ ] **Step 1: Banner the docs realignment plan**

Insert immediately after line 1 (`# Documentation Realignment Implementation Plan`)
and before the existing `> **For agentic workers:**` line:

```markdown

> **Superseded, 2026-07-30. Do not execute.** This plan's source document,
> `NEW_RULES.md`, was untracked and no longer exists, and its six references to
> `src/humansays/catalog.py` and `src/humansays/signals/` name modules deleted
> in phase C1. Its outcomes did land: the per-domain planned catalog is under
> `docs/site/planned/`, and the nine-phase roadmap retirement is recorded in
> `.agent-specs/roadmap-retirement.md`. Kept for provenance. If documentation
> realignment is wanted again, write a new plan against the current layout
> rather than reviving this one — its premises predate two phases that changed
> them.
```

- [ ] **Step 2: Banner the C1 plan**

Insert immediately after line 1 (`# Phase C1 — rule metadata relocation`) and
before the `## Context` heading:

```markdown

> **Executed and superseded, 2026-07-30.** The work landed on branch
> `chore/rules-relocation`. The **Context** and **Established Facts** sections
> below describe the tree *before* this plan ran: `src/humansays/catalog.py` and
> `src/humansays/signals/` were deleted by it and no longer exist. Read them as
> a record of what the author found, not as a description of the current
> layout. Phase C2 followed and is in
> `2026-07-30-phase-c2-disposition-model.md`.
```

- [ ] **Step 3: Verify every plan is now labelled**

```bash
for f in .agent-specs/plans/*.md; do
  printf '%-60s ' "$(basename "$f")"
  head -12 "$f" | grep -qi "superseded\|executed" && echo LABELLED || echo "NO BANNER"
done
```

Expected: `LABELLED` for `2026-07-26-docs-realignment.md`,
`2026-07-29-phase-b-extraction-split.md`, and
`2026-07-30-phase-c1-rule-metadata-relocation.md`.

`2026-07-27-test-suite-standardization.md`,
`2026-07-29-extraction-enforcer-gaps.md` and
`2026-07-30-phase-c2-disposition-model.md` may report `NO BANNER`. Do not add
one — the audit graded all three clean, and C2 is the plan this branch is
delivering. Report their status; do not act on it.

- [ ] **Step 4: Commit**

```bash
git add .agent-specs/plans/2026-07-26-docs-realignment.md \
        .agent-specs/plans/2026-07-30-phase-c1-rule-metadata-relocation.md
git commit -m "docs(specs): banner the two plans describing a tree that no longer exists"
```

---

## Task 8: Delete `scripts/check_scope.py`

**This task is independently rejectable. Approving Tasks 4–7 does not commit to
this one.** It is separated because the audit explicitly recorded that it had
established only that the script has no input, not that it should go.

The evidence for deletion:

- `ALLOWLIST_NAME = 'paths.json'` at `scripts/check_scope.py:34`, and
  `find . -name paths.json -not -path './.git/*'` returns nothing. The script's
  input does not exist.
- No hook, no CI workflow, and no other script invokes it. Verified by the grep
  in "Corrections to the audit" above.
- `scope-guard.md`, deleted in Task 4, recorded that its own test
  `tests/tooling/test_scope_guard.py` was removed when the guard became an
  agent-facing tool. So no test asserts its behaviour either.
- After Task 4, the only remaining prose describing how to use it is gone.

The evidence against, stated so a reviewer can weigh it:

- `docs/evidence/phase-1-cd-closeout.md:16` records "`scripts/check_scope.py`
  present" as a verified gate. That is a record of a past measurement, and
  deleting the file today does not falsify what was measured then. The evidence
  file is **not** edited by this task.
- The script encodes a real lesson — POSIX-like glob semantics where `*` does
  not cross `/`, and reading all four change sources. Task 4 preserves the
  four-sources lesson in prose. The glob implementation is recoverable from git
  if a future guard needs it.

**Files:**
- Delete: `scripts/check_scope.py`
- Modify: `.agent-specs/design/07-idea-register.md` (row 43)

**Interfaces:**
- Consumes: Task 4 must have committed first, or the deletion leaves
  `agent-protocol.md` §3 naming a script that is gone.
- Produces: nothing.

- [ ] **Step 1: Confirm Task 4 has landed**

```bash
grep -rn "check_scope" .agent-specs/process/
```

Expected: no output. If `agent-protocol.md` still names the script, stop and
finish Task 4 first.

- [ ] **Step 2: Confirm no consumer exists**

```bash
grep -rn "check_scope" --include='*' . 2>/dev/null | grep -v '^\./\.git/'
```

Expected hits, and nothing else:
- `scripts/check_scope.py` itself
- `.agent-specs/design/07-idea-register.md:43` — removed in Step 4
- `.agent-specs/roadmap-retirement.md:28` — a historical statement about what
  the phase roadmap used, left alone
- `docs/evidence/*` — measured records, left alone

Any hit in `.github/`, `scripts/` other than the file itself, or `tests/` means
this task is wrong. Stop and report it.

- [ ] **Step 3: Delete the script**

```bash
git rm scripts/check_scope.py
```

- [ ] **Step 4: Remove the idea-register row**

In `.agent-specs/design/07-idea-register.md`, delete line 43 entirely:

```markdown
| Working scope guard (`check_scope.py`) | 5 | 5 | S | **Phase 1.** Verified against seven bypasses |
```

- [ ] **Step 5: Verify the tree still passes every gate**

```bash
scripts/format.sh
uv run pytest
scripts/lint.sh
```

Expected: all pass, test count unchanged from Task 1's 326.

**No gate in `scripts/lint.sh` reads `scripts/`.** `pyproject.toml:117-118`
scopes vulture to `paths = ["src", "tests"]`, so a green vulture run says
nothing about this deletion — do not report it as if it did. The suite and the
import contracts are likewise blind to it. What establishes the deletion is
safe is Step 2's grep, not this step; Step 5 only confirms nothing else broke.

- [ ] **Step 6: Commit**

```bash
git add .agent-specs/design/07-idea-register.md
git commit -m "chore(scripts): delete the scope guard, whose allowlist input no longer exists"
```

---

## Task 9: Correct the design documents and prepare the PR

`design/00-overview.md` ends with a seven-phase roadmap table for a roadmap
retired in `roadmap-retirement.md`. It also carries a false enforcement claim:
"CI reports sections with zero coverage — that number, not the rule count,
measures how much of the document the tool enforces." No CI job does this.
`CLAUDE.md` rule 13 requires an enforcement claim to name its enforcer or be
written as convention, and rule 9 already states the philosophy-link pairing as
convention for exactly this reason.

`design/07-idea-register.md` scores 35 ideas against a **Phase** column
(`Phase 1` through `Phase 8`) that indexes a roadmap that does not exist. Row 9
says "Delete `PY010`/`PY011`", which happened — those are the retired HS010 and
HS011.

The register is itself backlog-shaped, and the operator's directive arguably
kills it too. It is kept because it is a design reference carrying impact and
confidence scores rather than a work queue, and converting it is a larger change
than this plan's scope. **Flag this tension in the PR body**; do not resolve it
here.

**Files:**
- Modify: `.agent-specs/design/00-overview.md:47-68`
- Modify: `.agent-specs/design/07-idea-register.md` (column header and every
  row's phase reference)
- Create: `/tmp/claude-1000/-home-rhawk-dev-humansays/bd31e2db-b120-49b3-8063-c2d1c4146d89/scratchpad/pr-body.md`

**Interfaces:**
- Consumes: every prior task, since the PR body describes all of them.
- Produces: a PR body on disk. **This task does not open the PR.**

- [ ] **Step 1: Fix the false enforcement claim in the overview**

Replace:

```markdown
The rules are an attempt to programmatically enforce two authored documents:
*Python Code Design and Review Criteria* and *Rust Code Design and Review
Criteria*. Every rule cites a section. CI reports sections with zero coverage —
that number, not the rule count, measures how much of the document the tool
enforces.
```

with:

```markdown
The rules are an attempt to programmatically enforce two authored documents:
*Python Code Design and Review Criteria* and *Rust Code Design and Review
Criteria*. Every rule should cite a section, and how much of the document is
covered — not the rule count — is what measures how much the tool enforces.

**Nothing checks the citation.** It is convention, per `CLAUDE.md` rule 9. The
19 shipped rules satisfy it because each page under `docs/site/rules/` links the
`docs/site/philosophy/` page its criteria come from and each of those links
back, but no test or CI job reads that pairing, and no job counts uncovered
sections. The 175 planned rules under `docs/site/planned/` carry no criteria
citation at all.
```

- [ ] **Step 2: Delete the dead roadmap table**

Delete the whole `## Roadmap` section from `design/00-overview.md` — the heading
and the seven-row table — and replace it with:

```markdown
## Roadmap

There is no roadmap. The nine-phase structure this section described was retired;
[`../roadmap-retirement.md`](../roadmap-retirement.md) records the
phase-by-phase disposition. Only the next piece of work gets planned, and plans
live in [`../plans/`](../plans/).
```

- [ ] **Step 3: Rewrite the idea register's phase column**

In `.agent-specs/design/07-idea-register.md`, the final column is headed
`Verdict` and currently mixes a phase assignment with a note. **The header row
does not change** — `| Idea | Feas | Value | Effort | Verdict |` stays exactly
as it is. Only each data row's final cell changes, dropping the phase
assignment while keeping the note.

Apply this transformation to every row, deleting the bolded phase clause and
keeping the rest verbatim. Worked examples:

| Before (final cell) | After (final cell) |
|---|---|
| `**Phase 2, task 1.** Prototyped; fixes a proven correctness bug` | `Prototyped; fixes a proven correctness bug` |
| `**Phase 1.** Measured: 26% faster, 61% quieter, identical score` | `Done. Measured: 26% faster, 61% quieter, identical score` |
| `**Phase 5 Layer 4, only if the gate demands it.** 13x slowdown` | `Only if the effect gate demands it. 13x slowdown` |
| `Phase 6. Nearly free` | `Nearly free` |
| `Any time after Phase 4. Validates the contract for the price of a toy` | `Validates the contract for the price of a toy` |

Rows are identified by their **Idea** cell, not by line number. Three describe
work that has shipped and are marked `Done.` rather than merely stripped:

- `Delete PY010/PY011` — done; retired as HS010 and HS011.
- `Drop pydantic-settings` — done; `dependencies = []` in `pyproject.toml`, with
  `deptry` in `scripts/lint.sh` as the enforcer.
- `Working scope guard (check_scope.py)` — Task 8 deletes this row outright. If
  Task 8 was rejected, keep the row but strip its `**Phase 1.**` clause like the
  rest.

Add immediately below the table:

```markdown
These are scored ideas, not scheduled work. Nothing here is planned, nobody is
assigned, and an entry sitting here for a year costs nothing. If one is worth
doing, it gets a plan under [`../plans/`](../plans/) and stops being an entry
here.
```

- [ ] **Step 4: Verify the phase vocabulary is gone from `design/`**

```bash
grep -rn "Phase [0-9]\|phase [0-9]\|## Roadmap" .agent-specs/design/
```

Expected: the only hit is the `## Roadmap` heading in `00-overview.md`, whose
body now says there is no roadmap. No `Phase N` reference anywhere in
`07-idea-register.md`.

```bash
grep -rn "CI reports sections" .agent-specs/
```

Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add .agent-specs/design/00-overview.md .agent-specs/design/07-idea-register.md
git commit -m "docs(specs): drop the dead roadmap and the CI claim nothing backs"
```

- [ ] **Step 6: Run the full gate one final time**

```bash
scripts/format.sh
uv run pytest
scripts/lint.sh
scripts/ci.sh docs
```

Expected: 326 tests pass, coverage at or above 97.33%, `scripts/lint.sh` exits
zero with all three import contracts intact, docs build succeeds under
`--strict`.

Then confirm the pre-existing working-tree modification never entered a commit:

```bash
git status --short
```

Expected: exactly `M scripts/check_commit_msg.py`, and nothing else.

```bash
git log --oneline --stat origin/develop..HEAD -- scripts/check_commit_msg.py
```

Expected: no output. If this returns a commit, the file was staged by accident;
stop and report it.

- [ ] **Step 7: Report the commit range — do not push**

Operator decision, 2026-07-30: **this plan commits but does not push.**
`CLAUDE.md` rule 8 is the governing statement — the operator owns git, and a
push is outward-facing on a branch with no PR open. Run:

```bash
git log --oneline origin/develop..HEAD
```

Report the range and the commit count. The operator pushes.

- [ ] **Step 8: Write the PR body to the scratchpad**

Write to
`/tmp/claude-1000/-home-rhawk-dev-humansays/bd31e2db-b120-49b3-8063-c2d1c4146d89/scratchpad/pr-body.md`:

```markdown
## What this is

Two related but separable pieces of work on one branch. The PR template asks
for one logical concern; this is two, kept together because the second depends
on the first's layout and splitting them would serialize review for no gain.

**C1 — rule metadata relocation. No behaviour change.** Rule metadata moved out
of `src/humansays/catalog.py` and the `signals/` package into per-group
`rules.toml` files under `src/humansays/rules/`. All 19 `HS0NN` identifiers are
unchanged; no threshold, severity, confidence or weight moved. Verified by a
byte diff of CLI output against a baseline captured before the change, empty at
every commit.

**C2 — the disposition model. Behaviour changes.** Rules gained a `disposition`
of `on | hint | evidence | off`. HS015, HS016 and HS021 are now `hint`: still
reported, no longer weighed. `--show-evidence` reveals `evidence` findings.
JSON output carries a new key.

**Scores move, and so does the exit code.** A file whose only findings are
HS015, HS016 or HS021 now scores clean where it did not before. Recorded in
`CHANGELOG.md` under Unreleased → Changed.

**Specs cleanup.** `.agent-specs/backlog.md` is deleted — the project has
stopped keeping a backlog. Its four measurements were relocated to
`docs/evidence/backlog-measurements.md` first. The retired per-phase machinery
(`paths.json` allowlists, `PHASE.md`, `scripts/check_scope.py`) is gone from the
protocol and the tree; none of it had an input, a caller, or a test.

## Verification

| Gate | Command | Result | Cannot see |
|---|---|---|---|
| Suite | `uv run pytest` | 326 pass, 97.33% | anything the fixtures do not exercise |
| Lint | `scripts/lint.sh` | zero | runtime behaviour |
| Docs | `scripts/ci.sh docs` | builds under `--strict` | whether a page is true |
| Sweep guards | `mv corpus corpus.bak && uv run pytest` | fails as designed | a corpus that is present but thin |

All run on one interpreter, locally. **CI has never run on this branch.** The
matrix is 3.11–3.14 plus a wheel smoke and the docs build.

## Known open, not addressed here

- **`docs/site/` still says `0.1.0a1` in twelve places** while `pyproject.toml`
  and the `v0.1.0a2` tag say otherwise. That is a release-documentation
  question, not a specs one, and fixing it inside this branch would mix a third
  concern into a PR that already carries two.
- **`.agent-specs/design/07-idea-register.md` is backlog-shaped.** Its phase
  column is gone and it is now explicitly labelled "scored ideas, not scheduled
  work", but if the no-backlog rule is meant to reach it, it should go too.
  Left standing pending a call.
- **`.agent-specs/process/agent-protocol.md` §4c row 1 is struck, not
  replaced.** The `.migration/capture.sh` byte-diff gate is gone and nothing
  covers what it covered.
```

- [ ] **Step 9: Hand off**

Report to the operator:
- the PR body's path
- the commit range from Step 7, and that the branch is **not pushed**
- the three "Known open" items, so the decision to push and open the PR is made
  with them visible

**Do not push and do not open the PR.** `CLAUDE.md` rule 8: the operator owns
git, and both are outward-facing.

---

## Task ordering

Tasks 1, 2, 3 and 5 are independent and can run in any order or in parallel.

Hard dependencies:
- **Task 6 requires Task 2 committed.** Deleting `backlog.md` before its
  measurements are relocated loses them.
- **Task 8 requires Task 4 committed.** Deleting the script before the protocol
  stops naming it leaves a dangling reference.
- **Task 9 Steps 6–9 require every other task committed.** They are the final
  gate and the push.

Task 7 and Task 9 Steps 1–5 have no dependencies but are cheapest last, since
Task 9's verification greps assert the end state of Tasks 4, 6 and 8.

## What this plan does not investigate

- Whether the `docs/site/` `0.1.0a1` occurrences should become `0.1.0a2`. Some
  are transcripts of installation output and would be falsified by editing;
  some are live version claims. Distinguishing them requires knowing what is
  actually on PyPI, which was not checked.
- Whether `design/07-idea-register.md` should be deleted under the no-backlog
  rule. Task 9 relabels it and flags the question.
- Whether `roadmap-retirement.md` needs editing. The audit graded it clean;
  Task 6 Step 5 checks only its `backlog.md` link.
- Whether the three plans left without banners in Task 7 Step 3 should have
  them. Reported, not acted on.
- Anything about the CI matrix. It has never run on this branch and this plan
  does not make it run.

---

## Appendix: the commands behind every claim

Run on `chore/rules-relocation`, 2026-07-30. Output is quoted as returned.

Two commands in the research session that produced this plan **failed and
produced nothing**, and are listed because their absence is why several claims
went unbacked until this appendix was written:

- `ls CHANGELOG* 2>&1` — zsh `no matches found`, exit 1. It sat in an `&&`
  chain, so the three greps after it never ran.
- `grep -rn "vulture" .vulture* pyproject.toml` — zsh `no matches found`, exit
  1. No `.vulture*` file exists; the config is a `pyproject.toml` table.

### No `paths.json` exists anywhere in the tree

Underwrites: Task 4 (deleting §3/§3a), Task 8, the Established facts section.

```bash
find . -name paths.json -not -path './.git/*'
```

No output, exit 0. Every document describing a phase allowlist describes a file
that is not there.

### `scripts/check_scope.py` has no caller, no hook, no CI job

Underwrites: Task 8.

```bash
grep -rn "check_scope" --include='*' . 2>/dev/null | grep -v '^\./\.git/'
```

Seven hits, all prose: `design/07-idea-register.md:43`,
`process/agent-protocol.md:33,58`, `process/scope-guard.md:21,26`,
`roadmap-retirement.md:28`, `backlog.md:37`, plus `docs/evidence/*` historical
records. Zero hits in `.github/`, `tests/`, or any other script. Combined with
the `find` above, the script has neither an input nor an invoker.

### No CI workflow references the retired phase machinery

Underwrites: the "Corrections to the audit" section — this is the question the
audit recorded as *not investigated*.

```bash
ls .github/workflows/
grep -rn "phases/\|paths.json\|check_scope\|philosophy" \
     .github/workflows/ scripts/ci.sh scripts/lint.sh
```

Seven workflows exist (`build-package`, `ci-playbook`, `deploy-site`,
`integration`, `release`, `security-audit`, `upload-mkdocs`). The grep returns
**no output** — no workflow and neither quality script names a phase path, an
allowlist, the scope script, or the philosophy pairing.

That is also the proof that `design/00-overview.md`'s claim "CI reports sections
with zero coverage" names an enforcer that does not exist. Task 9 Step 1 fixes
it.

### The review checklist's step 1 is unsatisfiable

Underwrites: Task 5.

```bash
grep -rn "What a wrong implementation" . 2>/dev/null | grep -v '^\./\.git/'
```

```
.agent-specs/process/agent-protocol.md:179
.agent-specs/process/review-checklist.md:7
```

Both are the *instruction* to open such a section. No plan under
`.agent-specs/plans/` contains the phrase, so the section the reviewer is sent
to has never existed. (Hits inside this file are it quoting the problem.)

### `.migration/` is gone and gitignored

Underwrites: Task 4 Step 4 (§4c row 1), Task 2's closing note.

```bash
ls -d .migration                 # No such file or directory
grep -n "migration" .gitignore   # 222:.migration/
```

### Both version tags exist; `pyproject` and the docs disagree

Underwrites: Task 6, and the "known open" item in Task 9's PR body.

```bash
git tag --list | tail -10        # v0.1.0a1, v0.1.0a2
grep -n version pyproject.toml   # 3:version = "0.1.0a2"
git log --oneline -3 -- pyproject.toml
                                 # dee4838 release(version): bump to 0.1.0a2
grep -rn "0\.1\.0a1" .agent-specs/ docs/ README.md
grep -n "0\.1\.0a1" CLAUDE.md    # 86:  `0.1.0a1` ships 19. ...
```

Three occurrences are in scope for Task 6: `.agent-specs/README.md:13`,
`.agent-specs/CLAUDE.md.template:85`, and `CLAUDE.md:86`.

Twelve more are under `docs/site/` and are **out of scope**, because they are
not all the same kind of statement. `getting-started.md:21` reads
`Successfully installed humansays-0.1.0a1` — a transcript, which editing would
falsify. `rules/index.md:10` reads "Version `0.1.0a1` ships 19 rules" — a live
claim, now wrong. Distinguishing them needs to know what is actually published,
which was not checked. Task 9's PR body raises it.

`roadmap-retirement.md:31` and `docs/evidence/*` are historical and correct as
they stand.

### The three surveys pass while examining nothing

Underwrites: Task 1.

```bash
grep -n "^CORPUS\|^MANIFEST\|from tests.fixtures" \
  tests/unit/test_rule_registry.py tests/unit/test_rule_messages.py \
  tests/golden/test_parity.py
grep -rn "sweeps" tests/
```

`tests/fixtures/sweeps.py` is imported by five modules —
`test_import_contract_coverage`, `test_analysis_confinement`,
`test_cli_contract`, `test_planned_catalog`, `test_sweep_helpers`. The three in
Task 1 import `tests.fixtures.sources` but **not** `sweeps`, and each builds its
own corpus:

- `test_rule_registry.py:41` and `test_rule_messages.py:29` both define
  `CORPUS = Path(__file__).resolve().parents[1] / 'golden/poc-parity/corpus'`
  and walk it with a raw `sorted(CORPUS.rglob('*.py'))`.
- `test_parity.py:37` loads `MANIFEST` from `manifest.toml`, and
  `_group_names()` returns `list(MANIFEST['groups'])` with no floor.

`sweeps.py`'s own docstring names this shape as having "already shipped twice in
this repository" and says "every one of them comes through here." These three do
not. `tests/unit/test_sweep_helpers.py:14,16` already imports `pytest` and
`matching, python_sources`, which is why Task 1 Step 1 only extends the import.

### No gate in `scripts/lint.sh` reads `scripts/`

Underwrites: Task 8 Step 5.

```bash
grep -n -A4 'tool.vulture' pyproject.toml
```
```
117:[tool.vulture]
118-paths = ["src", "tests"]
```

Vulture is the only lint check that could plausibly notice a dead script, and it
does not scan `scripts/`. A green run after Task 8 is not evidence about the
deleted file.

### Three backlog claims were false, and are recorded as false

Underwrites: Task 6's list of corrections.

```bash
grep -n "DOWNSTREAM_PACKAGES" tests/integration/test_analysis_confinement.py
```
```
71:DOWNSTREAM_PACKAGES = ('facts', 'rules')
```
The backlog said `facts` or `signals`. `signals` was deleted in C1.

```bash
wc -l src/humansays/rules/loading.py     # 205
grep -n "^def \|^_" src/humansays/rules/loading.py
```
205 lines, not 195, and `_disposition` at line 113 is absent from the entry's
function list — it was added by C2, after the entry was written.

```bash
grep -n "HS010\|HS011\|HS020" docs/site/rules/index.md
```
```
106:## The gaps at HS010, HS011, and HS020
112:- `HS010`, comment counting. ...
114:- `HS011`, docstring counting. ...
116:- `HS020`, `from __future__ import annotations`. ...
```
The backlog said the vacant IDs "suggest rules were dropped without a record."
There is a record, with a reason for each.

### The plan that is bannered rather than deleted

Underwrites: the "Corrections to the audit" section.

```bash
sed -n '1,12p' .agent-specs/plans/2026-07-29-phase-b-extraction-split.md
```
Lines 3–8 are a superseded banner naming commit `41ceb74` and the plan that
inherited its gaps, ending "Kept for provenance; do not execute it." The audit
graded it deletable. It is already doing the job an archived plan should.

```bash
grep -n -i "changelog" .agent-specs/plans/*.md
```
One hit — `2026-07-30-phase-c2-disposition-model.md:110` — the obligation Task 3
discharges.

### Numbers this plan did **not** verify

`uv run pytest` and `scripts/lint.sh` were never run in the session that wrote
this plan. The figures it quotes — **324 tests**, **97.33% coverage**, three
passing import contracts, a clean `scripts/ci.sh docs` — come from the
operator's briefing, not from a command whose output is recorded here.

Task 1 Step 8 expects **326** on the arithmetic that it adds two tests to 324.
If the pre-change count is not 324, that is the first thing to reconcile, and
the expectation in Step 8 is what is wrong, not the suite.
