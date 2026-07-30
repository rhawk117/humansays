# Agent protocol

How work is executed in this repository. Applies to every phase.

## 1. One phase per session

A session executes tasks from exactly one `PHASE.md`. Do not read other phase
files. They describe work that is deliberately deferred, and reading them
reliably produces scope drift.

## 2. Acceptance tests come first

For any task with a non-trivial correctness condition:

1. Write the failing test from the phase document.
2. Run it and confirm it fails for the stated reason -- not on an import
   error or a typo.
3. Commit it red: `fix(scope): add failing test for <condition>`. A red
   acceptance test is a valid checkpoint; the tree is green when the suite's
   failures are exactly the ones the phase document predicts.
4. Make it pass, and commit that separately.

Models are substantially better at "make this red test green" than at
"implement this specification". Committing the red test yourself preserves
that split without routing through the operator.

## 3. Scope

Every phase directory contains `paths.json`:

    {"note": "...", "allowed": ["src/**"], "deny": ["src/runtime/**"]}

`uv run python scripts/check_scope.py <phase> --base develop` reports any
change outside it, reading committed, staged, unstaged and untracked files.

**No hook and no CI job runs this.** It is enforcement by obligation: run it
at every task boundary, before every commit. A violation is not something to
work around -- stop, report the path and why it is needed, and wait. See
[`scope-guard.md`](scope-guard.md).

## 3a. Allowlists are derived, not inherited

The original allowlists were authored at roadmap time against a repository
layout that did not exist yet. This is not hypothetical: Phase 2's allowlist
denied the criteria document that Phase 2's own acceptance test requires.

At phase start, derive the allowlist from the actual tree:

1. List every symbol the phase changes, from `PHASE.md`.
2. Search for every consumer of every one of those symbols.
3. The allowlist is the set of files that search returns, plus the phase's
   own directory.
4. **Put the search output in the commit body** that establishes the
   allowlist. A reviewer needs to see what was searched for, not only what
   the result was.

Mid-phase additions keep the widening ritual: an allowlist change lands in a
commit containing nothing else, with a one-line reason. `check_scope.py`
reports violations of that isolation rule, though it does not block them --
see §3.

## 4. Constraints that can be tests, are tests

The documents are the source you write checks *from*. Once written, the checks
enforce — not your memory of the document.

| Constraint | Enforcement |
|---|---|
| Zero runtime dependencies | `deptry` |
| `ast` confined to `analysis/` | `lint-imports` |
| Behavior-preserving migration | parity golden fixtures |
| Argument-kind correctness | `tests/criteria/` fixture pair |
| Doc and catalog agree | catalog validation test |
| Observed findings never aggregate | scorecard input assertion |
| New code under `src/humansays` emits no weighted finding | `tests/golden/test_self_scan.py` |

If you are about to rely on remembering a constraint, write the check instead.

The self-scan row is the one plans keep missing, so it is worth stating in
prose too. `tests/golden/test_self_scan.py` is an **exact match** against a
committed baseline of humansays scanning its own source. Any module added to or
moved within `src/humansays` that produces a weighted finding fails it. A phase
that adds modules under `src/` therefore has a constraint on the shape of the
code it writes, not only on its behavior: either the new code is clean by the
tool's own rules, or the baseline gains an entry with a stated reason. Learn
this before writing the code, not from a red test afterwards.

## 4a. Every enforcement claim names its test

If a document says a mechanism prevents, blocks, or guarantees something,
that sentence must name the test, hook, or CI job that demonstrates it. A
claim with no named enforcer has not been checked, and must be written as
convention rather than as enforcement.

This exists because it has already failed twice. The scope guard was
documented as physically blocking signature changes, and a six-line test
showed it blocked nothing. It was then documented as running "as a
pre-commit hook and in CI" while being invoked by neither.

Phrases worth auditing hardest: *physically blocked*, *all mechanical*,
*complete*, *exact*, *only path*, *cannot happen*, *the gate proves*.

## 4b. Plans live in the repository

`.agent-specs/plans/`, named `YYYY-MM-DD-topic.md`, committed with the code they
change. Not a home directory, not an agent harness's private state directory.

A plan outside the tree cannot be reviewed against §4's constraint table before
someone executes it, and cannot be diffed against the phase that follows it.
Both costs have been paid: the C1 plan assigned modules to packages without
checking the import direction that already existed between them, which made two
of its tasks unexecutable as sequenced and was discovered only at execution
time, by a broken contract.

A plan keeps its **discovered-during-execution** section. That section is the
part with the highest value per line to the next plan's author, because it
records what the tree turned out to be rather than what the plan assumed.

## 4c. Every gate states what it is blind to

A verification section that lists gates without saying what each one cannot see
produces a green run over a real defect. This is not hypothetical: every defect
C1 produced was a check that passed without looking.

| Gate | Cannot see |
|---|---|
| Byte-diff of scan output | whether the tests still test the same things |
| Coverage | a test that reads source files as data, whose input set shrank |
| A collision or uniqueness survey | a registration its corpus never fired |
| `lint-imports` | a contract stanza that enumerates by hand and fails open |
| `tests/golden/test_self_scan.py` | anything outside `src/humansays` |

Write the blind spot next to the gate in the plan, then choose a second check
for anything the first one cannot reach. `tests/fixtures/sweeps.py` exists
because a sweep's empty result and its clean result are the same green tick.

## 5. Evidence discipline

Separate **verified**, **inferred** and **unknown**. Do not present an inference
as a measurement.

- No root-cause claim without a stack trace or source evidence
- No dependency change from version correlation alone
- No performance claim without a before/after measurement
- Numbers in `evidence/` are measured. Do not re-derive them from assumptions;
  if you believe one is wrong, re-run the measurement and report the delta

## 6. Adversarial review before merge

Every phase ends with a review pass that assumes the implementation is wrong.
See [`review-checklist.md`](review-checklist.md). The reviewer reads the phase
document's **"What a wrong implementation looks like"** section first and
attempts to confirm each failure mode before anything else.

## 7. What to do when blocked

Do not substitute an unverified theory. Mark the question unresolved, record
what you tried, and stop. A stopped task with a clear question is worth more
than a completed task built on a guess.

## 8. Git

Agents commit and push their own branch. Agents do not merge, rewrite, or
destroy.

**Permitted:** `status`, `diff`, `log`, `show`, `add`, `commit`, `checkout`,
`checkout -b`, `stash list`, `push`.

**Forbidden, without exception:** `merge`, `rebase`, `reset`, `revert`,
`cherry-pick`, `branch -m`, `tag`, `remote`, `worktree`, `clean`, and any
command containing `--force` or `-f`.

**`branch -D` has exactly one exception:** deleting a branch the agent itself
created in the same session with a `tmp/` prefix. Any other `branch -D` is
forbidden.

There is no other "unless asked" clause. An agent that believes it needs a
forbidden verb stops and reports what it wants to run and why. The operator
runs it.

`push` is permitted so the operator can follow along. Force-push is not,
which is what keeps every push recoverable. The forbidden list is the set of
verbs that destroy work or rewrite shared history; the permitted list is the
set that creates recoverable checkpoints.

### Commit conventions

- **One commit per step that leaves the tree green**, not one per task. A red
  acceptance test committed per §2 is a valid checkpoint.
- **Format:** `prefix(scope): summary`, prefix one of
  `feat|chore|ops|fix|release|docs`. Enforced by the `commit-msg` hook in
  `.pre-commit-config.yaml`, whose behavior is asserted by
  `tests/tooling/test_commit_msg.py`.
- **Branches** off `develop`, named `prefix/short-title`. Push each commit.
- **Squash merge** to `develop` as `prefix(short-title): summary [merges #N]`.
  Performed by the operator -- it requires `merge`, a forbidden verb.
- Run `scripts/precheck.sh` once per checkout before executing any phase. A
  hook that was never installed in a given checkout enforces nothing there.

### What is actually enforced

| Rule | Enforcer |
|---|---|
| Commit message format | `commit-msg` hook, asserted by `tests/tooling/test_commit_msg.py` |
| Hooks are installed | `scripts/precheck.sh`, if it is run |
| Scope stays inside `paths.json` | **nothing** -- §3, agent obligation |
| Allowlist derived from a search | **nothing** -- §3a, reviewer reads the commit body |
| Drift folded downstream before close | **nothing** -- §9, reviewer checks at merge |
| Forbidden git verbs | **nothing** -- §8, agent obligation |
| One commit per green step | **nothing** -- convention |

The bottom five rows are convention. They are listed so a reader knows which
lines the repository catches and which depend on the agent doing as told.
The commit-message hook is bypassable with `--no-verify`; no CI job backs it
up, because a CI rejection of an already-written commit leaves an agent no
remedy that §8 permits.

## 9. Phase close-out

A phase is not complete when its acceptance criteria pass. It is complete
when every drift and defect entry it produced has been applied to the
downstream phase documents it affects.

1. List every drift entry, defect, blocker, compromise and deferred decision
   the phase recorded.
2. For each, identify the downstream phase document it changes.
3. Apply the change to that document, **relocating the reasoning, not only
   the conclusion.** A deferred decision that arrives downstream without the
   argument for deferring it will be re-litigated or silently reversed.
4. Commit as `ops(phase-N): fold drift into downstream phase docs`.
5. **Only then** delete the entries. Deletion before relocation loses the
   reasoning permanently, because evidence is not tracked.

Evidence is per-phase and untracked -- working material, not an archive.
Anything that must outlive the phase belongs in a phase document before the
phase closes.
