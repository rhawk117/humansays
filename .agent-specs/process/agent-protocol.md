# Agent protocol

How work is executed in this repository. Applies to every phase.

## 1. One plan per session

A session executes tasks from exactly one plan under [`plans/`](../plans/). Do
not read the other plans. They describe work that is either finished or
deliberately deferred, and reading them reliably produces scope drift.

A plan carrying a **Superseded** banner is provenance, not work. Do not execute
it, and do not treat its "Established facts" section as describing the current
tree.

## 2. Acceptance tests come first

For any task with a non-trivial correctness condition:

1. Write the failing test from the plan.
2. Run it and confirm it fails for the stated reason -- not on an import
   error or a typo.
3. Commit it red: `fix(scope): add failing test for <condition>`. A red
   acceptance test is a valid checkpoint; the tree is green when the suite's
   failures are exactly the ones the plan predicts.
4. Make it pass, and commit that separately.

Models are substantially better at "make this red test green" than at
"implement this specification". Committing the red test yourself preserves
that split without routing through the operator.

## 3. Scope

A plan states the files it touches. Changing anything outside that set is scope
drift, and the remedy is to stop and report the path and why it is needed, not
to widen the plan mid-execution.

**Nothing enforces this.** The reviewer reading the diffstat against the plan's
file list is the check.

If a scope check is ever built: `git diff BASE...HEAD` sees only committed
changes, and a guard reading it alone is bypassed by anything staged, unstaged,
or untracked. A scope check that does not read all four sources is not a scope
check.

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

**Count gates by what they consume, not by which command runs them.** Two pairs
below read the same thing, which is the difference between six independent
checks and four.

| # | Gate | Consumes | Cannot see | Shares its input with |
|---|---|---|---|---|
| 1 | `tests/golden/test_self_scan.py` | the tool scanning `src/humansays` | anything outside `src/humansays`; unweighted findings | **2** |
| 2 | `test_cli_contract.py`, three assertions | the tool scanning `src/humansays`, via one `package_findings` dict | same blind spots as 1, and an empty dict satisfies all three at once | **1** |
| 3 | `tests/golden/test_parity.py` | the prototype `.raw.json` oracle | any rule the prototype never had, including the three retired ids | — |
| 4 | `test_specs_match_frozen_metadata` | literals frozen in the test file | whether those literals were transcribed correctly in the first place | **5** |
| 5 | `test_review_questions_match_poc_oracle` | the vendored prototype `catalog.py` | fields the prototype does not carry: severity, confidence, weight | **4** |
| 6 | `lint-imports` + `test_import_contract_coverage.py` | the module graph, and `.importlinter.ini` as text | a `layers` stanza, which the coverage test does not read; a hand-enumerated contract fails open | — |

Ambient and easy to overcount as coverage: `deptry` sees only declared-versus-
imported, and line coverage cannot see a test that reads source files *as data*
— its input set can halve without moving a covered line.

Two lessons, both from the table rather than from prose:

**Rows 1 and 2 are one gate wearing two names.** Both scan the same tree with
the same tool. If that scan returned nothing, four assertions go green together.
Row 2 is worse on its own: three assertions fed by one `package_findings` dict
is a single point of failure that looks like three, and it read as three in the
C1 plan's verification section. Count assertions by their input, not by their
`def`.

**Rows 4 and 5 were chosen well.** The frozen literals cannot check themselves,
so an independent transcription of the same 19 review questions checks them —
different source, different failure mode. That is what a second check is for,
and it is the only pair in the table that was deliberate rather than accidental.

So: write the blind spot next to the gate, write what each gate shares an input
with, and add a second check with a *different* input for anything the first
cannot reach. Two gates over one container are one gate.
`tests/fixtures/sweeps.py` exists because a sweep's empty result and its clean
result are the same green tick.

## 5. Evidence discipline

Separate **verified**, **inferred** and **unknown**. Do not present an inference
as a measurement.

- No root-cause claim without a stack trace or source evidence
- No dependency change from version correlation alone
- No performance claim without a before/after measurement
- Numbers in `evidence/` are measured. Do not re-derive them from assumptions;
  if you believe one is wrong, re-run the measurement and report the delta

## 6. Adversarial review before merge

Every plan ends with a review pass that assumes the implementation is wrong.
See [`review-checklist.md`](review-checklist.md). The reviewer starts from the
plan's verification commands and runs them, rather than reading the plan's
account of having run them.

## 7. What to do when blocked

Do not substitute an unverified theory. Mark the question unresolved, record
what you tried, and stop. A stopped task with a clear question is worth more
than a completed task built on a guess.

## 8. Git

The operator owns git. `CLAUDE.md` rule 8 is the governing statement and this
section elaborates it rather than qualifying it: an agent commits, branches or
pushes **only when asked**, and never merges, rewrites, or destroys.

The permitted list below is what an agent may run *once asked*. It is not a
standing permission.

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

`push`, when asked, is permitted so the operator can follow along. Force-push is
not,
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
| Scope stays inside the plan's file list | **nothing** -- §3, reviewer reads the diffstat |
| Drift folded into the plan before close | **nothing** -- §9, reviewer checks at merge |
| Forbidden git verbs | **nothing** -- §8, agent obligation |
| One commit per green step | **nothing** -- convention |

The bottom four rows are convention. They are listed so a reader knows which
lines the repository catches and which depend on the agent doing as told.
The commit-message hook is bypassable with `--no-verify`; no CI job backs it
up, because a CI rejection of an already-written commit leaves an agent no
remedy that §8 permits.

## 9. Plan close-out

A plan is not complete when its acceptance criteria pass. It is complete when
every drift and defect entry it produced has been written back into the plan
itself, under its **discovered-during-execution** section. The plan that
produced the finding is where the finding lives, because the next plan's author
reads the last plan and nothing else.

1. List every drift entry, defect, blocker, compromise and deferred decision
   the plan recorded.
2. Write each into the plan's **discovered-during-execution** section,
   **recording the reasoning, not only the conclusion.** A deferred decision
   recorded without the argument for deferring it will be re-litigated or
   silently reversed.
3. If a measurement was taken, it goes to `docs/evidence/` instead, because
   plans are not re-run and measurements are.
4. Commit as `ops(<topic>): fold execution findings into the plan`.
5. **Only then** delete the entries. Deletion before relocation loses the
   reasoning permanently.

Working material is untracked and disposable. Anything that must outlive the
plan belongs in the plan, or in `docs/evidence/` if it is a number, before the
plan closes.
