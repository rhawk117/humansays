# Adversarial review checklist

The reviewer assumes the implementation is wrong. Confirm or refute, in order.

## 1. Failure modes first

Open the phase document's **"What a wrong implementation looks like"** section.
Attempt to confirm each listed failure before looking at anything else. These
are the specific mistakes predicted for this phase.

## 2. Scope

- [ ] `scripts/check-scope.sh <phase>` passes
- [ ] If `paths.json` was widened, it happened in its own commit with a
      stated reason
- [ ] No change addresses a non-goal listed in the phase document

## 3. Acceptance criteria

Split into two kinds. Both must be satisfied; they are satisfied differently.

**Machine-verifiable** — a command exits zero.

- [ ] Every such checkbox has a named command, and it was run
- [ ] Checks that were skipped are reported as skipped, never as passing

**Reviewer-verifiable** — requires judgement, and must be stated as a judgement.

Examples: whether wording overclaims audit-event coverage; whether a refactor's
rationale matches its motivating finding; whether a negative microfixture is
genuinely close to its positive.

- [ ] Each was reviewed by a person and the judgement recorded with a reason
- [ ] None was silently converted into a machine check that does not test it

**Enforcement claims.**

- [ ] Every phase-document sentence claiming a mechanism prevents or guarantees
      something names the test that demonstrates it, and that test exists

## 4. Evidence

- [ ] Every performance claim has a before/after measurement
- [ ] No number in the diff contradicts `docs/evidence/poc-baseline.md` without
      a recorded re-measurement
- [ ] Inferences are labelled as inferences

## 5. Standing constraints

- [ ] `deptry` passes, and `dependencies` in `pyproject.toml` is still empty.
      `deptry` catches an undeclared import; the empty list is convention
- [ ] `lint-imports`: both contracts pass
- [ ] No third-party code is imported in order to analyze it
- [ ] Nothing expensive was added to the scan path
- [ ] No observed evidence contributes to a printed aggregate
- [ ] Every new or changed rule links the `docs/site/philosophy/` page its
      criteria come from, and that page links back from its "What enforces
      this" section
- [ ] No claim of being faster than Ruff, more comprehensive than Pylint, or an
      objective definition of clean code

## 6. Rule changes specifically

- [ ] `severity`, `confidence` and `weight` in `src/humansays/catalog.py` match
      the rule's page under `docs/site/rules/` exactly
- [ ] `severity` is `WARNING` only where the syntactic condition is close to the
      concern the rule names; otherwise `ADVISORY`. There is no third level
- [ ] `confidence` comes from a fixture-corpus proportion, not from an estimate
- [ ] Every new rule has both a positive and a negative microfixture
- [ ] Every new finding has an independence test proving it does not fire on
      single-dimension evidence

## 7. Structural quality

Reviewed against the criteria under `docs/site/philosophy/`, the same document
the tool enforces.

- [ ] Responsibility, state ownership, effect boundaries
- [ ] Testability without patching global state
- [ ] Failure semantics explicit
- [ ] No ceremonial abstraction introduced

## 8. Verdict

State one of: **accept**, **accept with follow-ups**, **reject**. If rejecting,
name the specific acceptance criterion that fails. "Feels wrong" is not a
verdict.
