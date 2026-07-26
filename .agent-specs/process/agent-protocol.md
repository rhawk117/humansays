# Agent protocol

How work is executed in this repository. Applies to every phase.

## 1. One phase per session

A session executes tasks from exactly one `PHASE.md`. Do not read other phase
files. They describe work that is deliberately deferred, and reading them
reliably produces scope drift.

## 2. Acceptance tests come first, in a separate session

For any task with a non-trivial correctness condition:

1. Session A writes the failing test from the phase document and stops.
2. **The operator commits it red.** Agents do not commit — see §8. Session A
   reports the file it wrote; the operator reviews and commits.
3. Session B receives the committed red test and the task, and makes it green.

Models are substantially better at "make this red test green" than at
"implement this specification." The phase documents are written to make this
split easy — every task with a subtle condition names its acceptance test.

## 3. Scope is enforced mechanically

Every phase directory contains `paths.json`. `scripts/check_scope.py`
fails if the diff touches anything outside it.

This exists because prose non-goals do not survive contact with a helpful model
that has spotted a real bug in a file it was not asked to touch. See
[`scope-guard.md`](scope-guard.md).

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

If you are about to rely on remembering a constraint, write the check instead.

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

The operator owns git. Do not commit, push, rebase, or create branches unless
explicitly asked. Report what you changed and let the operator decide.
