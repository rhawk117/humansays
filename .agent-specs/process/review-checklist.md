# Adversarial review checklist

The reviewer assumes the implementation is wrong. Confirm or refute, in order.

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

## 2. Scope

Nothing enforces scope. The diffstat against the plan's file list is the check.

- [ ] `git diff --stat <base>...HEAD` touches no file outside the plan's
      **Files** blocks
- [ ] Every file the plan named as touched actually changed, or the plan says
      why it did not
- [ ] No change addresses a non-goal the plan lists

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

- [ ] Every sentence in the plan or the docs it changes claiming a mechanism
      prevents or guarantees something names the test, hook or CI job that
      demonstrates it, and that enforcer exists

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

- [ ] `severity`, `confidence` and `weight` in `src/humansays/rules/*/rules.toml` match
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
name the specific acceptance criterion that fails, and the command whose output
shows it failing. "Feels wrong" is not a verdict.
