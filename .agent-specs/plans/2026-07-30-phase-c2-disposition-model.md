# Phase C2 — disposition model

## Context

C1 relocated rule metadata into per-group `rules.toml` files and left every
shipped rule scored. Today a rule has exactly one axis of importance:
`Severity`, which is `WARNING` (weight 3.0) or `ADVISORY` (weight 1.0), and
every finding contributes `weight * confidence` to the score. There is no way
to express "emit this, but do not score it", and no way to express "collect
this, but do not show it unless asked".

C2 adds that second axis. `Disposition` is `on | hint | evidence | off`,
distinct from `Severity`, and it governs **whether a finding scores and whether
it is shown**. Severity keeps governing **how much it scores when it does**.

The planned catalog already depends on this distinction. `docs/site/planned/`
publishes 175 rules whose defaults use `hint` and `evidence`, and
`docs/site/planned/reconciliation.md` maps 13 of the 19 shipped rules onto one
of those two. None of it is expressible today.

### C2 against C3

C1's re-scoping split the remaining work in two. C3 applies the reconciliation
mapping in full: 10 demotions to `evidence`, 3 splits, and the renames. **C2
builds the mechanism and carries exactly three rules across it** — `HS015`,
`HS016` and `HS021`, the three the reconciliation maps to `hint`.

That is a deliberate departure from "mechanism first, apply later", and the
reason is recorded in `.agent-specs/backlog.md` against a different feature:
*a boundary with no divergence to normalize and no test that can fail is
speculative*. If all 19 rules stayed `on` through C2, then `hint`, `evidence`
and `off` would ship dormant, exercised only by test-only rule definitions, and
the first real exercise would be C3. Three rules is the smallest change that
gives `hint` a production instance and moves a real score.

`evidence` and `off` still have no shipped instance after C2. That is stated
rather than hidden: see **Blind spots** below.

## Decisions taken

Each of these was settled with the operator before planning. The alternatives
are recorded because without them the next reader re-opens the question.

### 1. `disposition` lives on `RuleSpec` and is published in JSON

`reporting/grouping.py:84` calls `dataclasses.asdict(finding.rule)`, so every
`RuleSpec` field becomes a key in every JSON signal object. C1 used this fact
in the opposite direction: it put `message` on a `RuleDefinition` wrapper
precisely so the JSON shape would not move.

C2 moves it on purpose. A consumer reading a finding with weight 3.0 that
contributed nothing to the score has no way to understand that from the payload
unless the disposition is in it. Inferring it from a zeroed weight is exactly
the kind of implicit contract that rots.

- *Rejected: on `RuleDefinition`, invisible to JSON.* Keeps the payload stable,
  but leaves the score unexplainable from the output.
- *Rejected: on `RuleSpec` but filtered out of `RuleView`.* Keeps the payload
  stable now, at the cost of `asdict` no longer round-tripping the dataclass.
  The comment at `reporting/grouping.py:79-81` already warns that `RuleView`
  and the dataclass must be edited together; adding a silent divergence between
  them is the failure that comment exists to prevent.

**This is a JSON schema change.** It is additive — no key is removed or
retyped — but it is a change, and `docs/site/output.md` must document it in the
same commit.

### 2. Byte-identity is given up, and replaced

C1's headline gate was an empty byte diff. C2 cannot have one: three rules stop
scoring, so the score moves on every fixture that contains a static method, a
lambda or a function-level import, and every JSON signal object gains a key.

The replacement is **a measured before/after table**, committed to
`docs/evidence/`, listing for each golden fixture: penalty, density, score and
grade before and after. The claim "only these three rules stopped scoring" is
then checkable arithmetic rather than an assertion. Per CLAUDE.md rule 11 the
numbers are measured, not derived.

The finding *list* does not change. Hints are still emitted and still shown, so
`test_parity.py`'s finding-tuple comparison must stay green untouched. Only the
score half moves. That asymmetry is the sharpest available signal that C2 did
what it said: if a finding tuple moves, something other than scoring changed.

### 3. Evidence citation is deferred

`--show-evidence` ships. Citation — supporting signals rendered beneath the
finding that cites them — does not.

Citation needs a citing finding, and there is none. `reconciliation.md:26` names
`ENCAP011` as the finding through which `HS006`'s concern resurfaces, and
`ENCAP011` is unimplemented. Designing a citation format against zero real
citers would specify a relation with no consumer to validate it. It is filed in
`.agent-specs/backlog.md` already ("Supporting signals reported as evidence
beneath the finding that cites them").

### 4. The review profile is deferred, and `hint` is shown by default

`reconciliation.md:11-13` defines a hint as "emitted by the review profile;
intentionally unweighted". There is no profile mechanism in the codebase —
verified: no `profile` flag in `config/loading.py:build_parser`, no field in
`config/models.py`. Building profile selection *and* the disposition model in
one phase makes the before/after score table ambiguous, because two things
would have moved.

So in C2 a hint is **emitted, shown, and unweighted**. Profile gating is C3's
or later. `.agent-specs/backlog.md` already carries two profile entries; this
plan adds nothing there.

The consequence is user-visible and must be in the changelog: after C2, a file
with only static methods and lambdas scores 100 while still printing findings.
That is the intended end state per reconciliation, arrived at one phase early
for these three rules.

## Disposition semantics

The full matrix. Only the first two rows have a shipped instance after C2.

| Disposition | Emitted | Counts toward score | Shown by default | Shown with `--show-evidence` |
|---|---|---|---|---|
| `on` | yes | yes | yes | yes |
| `hint` | yes | **no** | yes | yes |
| `evidence` | yes | **no** | **no** | yes |
| `off` | **no** | no | no | no |

`off` short-circuits at emission rather than at display, so an `off` rule costs
nothing to have. That also makes `off` the only disposition that changes the
finding list, which is why no shipped rule may take it in C2.

## Invariants

| # | Invariant | Enforcer |
|---|---|---|
| 1 | The finding list is unchanged on every fixture. Only scores move. | `tests/golden/test_parity.py` finding-tuple comparison, untouched |
| 2 | Exactly three rules change disposition, and they are HS015, HS016, HS021. | `tests/unit/test_rule_definitions.py::test_specs_match_frozen_metadata`, with the frozen table updated in the same commit |
| 3 | A `hint` or `evidence` finding contributes zero penalty. | `tests/unit/test_scoring.py`, new |
| 4 | An `evidence` finding is absent from default output and present under `--show-evidence`. | `tests/integration/test_cli_contract.py`, new, against a test-only rule definition |
| 5 | Every `SignalName` has a disposition, and the loader rejects an unknown one. | `tests/unit/test_rule_definitions.py`, extended |
| 6 | `RuleSpec` and `RuleView` carry the same fields. | `tests/unit/test_reporting_views.py`, new — see Task 2 |
| 7 | Zero runtime dependencies. | `deptry` in `scripts/lint.sh`; `dependencies = []` |

Do not describe any of these as enforced without naming the check above.

## Established facts

Verified by reading the tree on 2026-07-30. Re-run rather than trust.

- `src/humansays/enums.py:11-13` — `Severity` is a `StrEnum` with exactly two
  members. `SignalName` at lines 35-54. **No disposition-like enum exists.**
- `src/humansays/rules/loading.py:38-45` — `RULE_KEYS` is a frozen set of
  exactly six names. `_check_keys` at lines 112-119 rejects unknown *and*
  missing keys. **A `disposition` key in a `rules.toml` is a load error today**,
  so the loader change and the data change must land in one commit.
- `src/humansays/findings/models.py:50-69` — `RuleSpec` fields are `signal`,
  `severity`, `confidence`, `weight`, `review_question`. `penalty` is a property
  returning `weight * confidence` (lines 68-69). `__post_init__` bounds-checks
  at 57-61.
- `src/humansays/reporting/grouping.py:16-24, 78-86` — `RuleView` mirrors
  `RuleSpec` field for field; `create_signal` builds the payload with
  `dataclasses.asdict(finding.rule)` cast to `RuleView`. The comment at 79-81
  states both must be edited together, and **nothing enforces it** — that is
  what invariant 6 is for.
- `src/humansays/reporting/ansi.py:36-48` — text output reads only
  `signal['rule']['signal']` and `signal['rule']['severity']`. **A new
  `RuleSpec` field does not appear in text output without explicit wiring.**
- `src/humansays/scoring.py:27-38` — `penalty = sum(finding.rule.penalty for
  finding in result.findings)`, unfiltered. `result.findings` at
  `reporting/models.py:33-34` flattens every finding from every report
  unconditionally. **There is no filter anywhere in this chain.**
- `src/humansays/rules/evaluation.py:68-78` — `evaluate()` builds every
  emission, converts via `build_finding`, returns `sorted(..., key=sort_key)`.
  No disposition step exists.
- `src/humansays/rules/registry.py:93-105` — `build_finding` is the single
  construction site combining `rule_definitions()[emission.signal]` with an
  `Emission`.
- `src/humansays/config/loading.py:151-188` — `build_parser` holds every flag.
  There is no `--show-evidence` and **no notion of a profile anywhere**. A new
  flag needs an entry in `build_parser` *and* in `CLI_DESTINATIONS`
  (`const.py:134-151`) *and* a field on the matching settings dataclass.
- `src/humansays/config/models.py:81-95` — `Report` carries `format`, `limit`,
  `fail_on`, `min_score`. **No per-rule enable/disable exists.**
- `reconciliation.md:21-41` — of the 19 shipped rules: 4 stay `on`, 3 are
  `on (split)`, **10 become `evidence`**, **3 become `hint`** (HS015, HS016,
  HS021). No shipped rule maps to `off` (stated at lines 170-172).

### The parity oracle is coupled to the weights, and C2 breaks that coupling

The highest-risk fact in this plan, and it is not obvious from the test name.

`tests/golden/test_parity.py:49-51` computes the *expected* penalty from the
oracle's own recorded `weight * confidence` per finding, then compares against
`score_for` run over humansays' findings (line 92). Demoting three rules to
`hint` zeroes their contribution on humansays' side but **not** on the oracle's,
so parity fails on the score comparison while the finding list still matches.

`_transform_oracle` must therefore skip hint-disposition rules when summing.
Doing that is correct, and it also **weakens parity as an independent oracle for
those three rules** — after the change it asserts "we agree with the prototype
except where we deliberately differ". That is honest but it is less evidence
than it was, and it is why invariant 1 leans on the finding-tuple comparison
rather than the score.

## Tasks

Each task ends green: full suite, `scripts/lint.sh`, and `scripts/ci.sh docs`.
Run `scripts/format.sh` before `scripts/lint.sh`; never invoke ruff or ty
directly. Conventional commits per `scripts/check_commit_msg.py`: prefix one of
`feat|chore|ops|fix|release|docs`, lowercase summary, no trailing period.

**Task 1 — capture the before-state.** Before any change, capture every golden
fixture's score in both formats with `.migration/capture.sh` into
`.migration/phase-c2-baseline/`, and capture twice into separate directories and
`diff -r` them to prove the capture is reproducible. A non-empty diff means
pre-existing nondeterminism — stop and report. This baseline is not a pass
condition as it was in C1; it is the *input* to the before/after table.

**Task 2 — pin the RuleSpec/RuleView agreement, before changing either.**
Add `tests/unit/test_reporting_views.py` asserting
`set(RuleView.__annotations__) == {f.name for f in fields(RuleSpec)}`. Commit it
green against today's code. This is invariant 6, and it must exist *before* the
field is added, or the first thing the new field does is silently violate the
contract the comment at `grouping.py:79-81` describes. Same for
`ObservationView` if it is a similar cast.

**Task 3 — the enum and the loader.** Add `Disposition` to `enums.py` as a
`StrEnum` with four members. Add `disposition` to `RULE_KEYS`, to
`build_definition`, and to all eight `rules.toml` files with the value `"on"`.
Add `disposition` to `RuleSpec` and to `RuleView`. Update the frozen table in
`test_specs_match_frozen_metadata` to carry the new field, all `on`.

Every rule is still `on`, so **the score must not move in this task**. Verify
with a byte diff against the Task 1 baseline for the text format only — the
JSON format legitimately changes here, because every signal object gains the
key. That split verification is the point: text proves scoring did not move,
JSON is inspected by hand for exactly one added key.

Add loader error-path tests: unknown disposition value, missing key. Coverage
gate is `fail_under = 85` (`.coveragerc.ini`).

**Task 4 — the scoring filter.** Make `penalty` zero for anything that is not
`on`. Prefer filtering in `scoring.py` over filtering in `evaluate()`: a hint
must still reach the report to be displayed, so removing it from
`result.findings` would be wrong. Add `tests/unit/test_scoring.py` covering each
disposition. Still no rule is anything but `on`, so **the score still must not
move**; this task is provably inert and that is what makes it reviewable.

**Task 5 — demote the three hints.** Change `disposition` to `"hint"` for HS015
(`yagni/rules.toml`), HS016 (`smell/rules.toml`) and HS021 (`idiom/rules.toml`).
Update the frozen metadata table. Update `_transform_oracle` in
`test_parity.py` to skip hint rules when summing the oracle penalty, with a
comment naming this plan and stating what the change costs.

The self-scan baseline (`tests/golden/self-scan-baseline.json`) needs checking:
its six entries are HS002 findings in `cli.py` and `reporting/ansi.py`, so it
is *probably* untouched, but `test_self_scan_matches_baseline_exactly` is an
exact match and must be run, not reasoned about.

Produce the before/after table into `docs/evidence/phase-c2-scores.md` from the
Task 1 baseline and a fresh capture. Every score change must be arithmetic:
old penalty minus the summed `weight * confidence` of the three demoted rules'
findings equals the new penalty, per fixture.

**Task 6 — `--show-evidence` and the evidence filter.** Add the flag to
`build_parser`, `CLI_DESTINATIONS`, and a `show_evidence` field on `Report`.
Filter `evidence`-disposition findings out of the displayed set unless the flag
is set — in the reporting layer, not in `evaluate()`, for the same reason as
Task 4.

No shipped rule is `evidence`, so this is tested against a **test-only rule
definition** rather than a shipped one. Build that fixture explicitly and say
in the test docstring that it is synthetic and why. Add the CLI test for
invariant 4.

**Task 7 — docs.** `docs/site/output.md` gains the new JSON key and the
disposition semantics table. `docs/site/rules/index.md` gains disposition as a
seventh `rules.toml` key and must stop saying every rule is scored — it
currently states the score contribution as unconditional. `docs/site/cli.md`
gains `--show-evidence`. `validation.omitted_files` is `warn` and the build runs
`--strict`, so any new page needs a `nav:` entry in `docs/mkdocs.yml` in the
same commit; no new page is planned. Enforcer: `scripts/ci.sh docs`, which runs
inside `make ci`.

**Task 8 — verify and report.** Full suite, `scripts/lint.sh`, `scripts/ci.sh
docs`. Name each `lint-imports` contract individually. Confirm `deptry` reports
no undeclared imports and `dependencies` is still `[]`. Show the before/after
score table. Delete `.migration/`.

## Verification

Gates counted by what they consume, per `process/agent-protocol.md` §4c.

| # | Gate | Consumes | Cannot see | Shares its input with |
|---|---|---|---|---|
| 1 | Text-format byte diff vs Task 1 baseline | CLI text stdout over the golden corpora | the JSON schema change, deliberately; anything the corpora do not exercise | 2 |
| 2 | Before/after score table | the same corpora, score fields only | a finding that moved without changing any score | 1 |
| 3 | `test_parity.py` finding tuples | the prototype `.raw.json` oracle | scoring, after Task 5 edits the transform | 4 |
| 4 | `test_parity.py` score comparison | the same oracle, with hints now excluded on both sides | whether excluding hints from the oracle was itself correct | 3 |
| 5 | `test_self_scan.py` | the tool scanning `src/humansays` | anything outside `src/humansays`; unweighted findings — **and after C2, hints are unweighted** | 6 |
| 6 | `test_cli_contract.py` self-scan assertions | the same scan, via one `package_findings` dict | same blind spots as 5; an empty dict satisfies all its assertions at once | 5 |
| 7 | `test_specs_match_frozen_metadata` | literals frozen in the test file | whether the literals were transcribed right | 8 |
| 8 | `test_review_questions_match_poc_oracle` | the vendored prototype `catalog.py` | severity, confidence, weight, disposition — it only covers review questions | 7 |
| 9 | `test_reporting_views.py` (new, Task 2) | `RuleSpec` and `RuleView` annotations | whether the JSON *values* are right, only that the key sets match | — |

Rows 3 and 4 are the pair to watch. They read the same oracle, and Task 5 edits
the transform that feeds row 4. **After Task 5, row 4 can no longer fail for the
three demoted rules**, which is exactly why invariant 1 is pinned on row 3.

Rows 5 and 6 are one gate wearing two names, carried forward from C1's §4c
table. Worse in C2 than in C1: `test_self_scan.py` is documented as catching
weighted findings, and Task 5 makes three rules unweighted. **A new HS015,
HS016 or HS021 finding in `src/humansays` will stop failing the self-scan after
C2.** Decide in Task 5 whether that is acceptable or whether the baseline test
needs to assert on unweighted findings too; do not leave it undecided.

```bash
# Before any change
.migration/capture.sh .migration/phase-c2-baseline

# After each task
uv run pytest
scripts/format.sh && scripts/lint.sh
scripts/ci.sh docs
```

## Blind spots, stated

- **`evidence` and `off` ship with no production instance.** Both are exercised
  only by test-only rule definitions. If the synthetic fixture drifts from how a
  real rule would be defined, nothing catches it until C3.
- **`off` is untested against the finding list.** It is the only disposition
  that changes what is emitted. No shipped rule may take it in C2, so the
  finding-list invariant cannot be violated — and equally cannot be exercised.
- **The review profile does not exist**, so "emitted by the review profile" is
  approximated by "shown by default". C3 or later must revisit whether hints
  should be hidden outside a review run.
- **Parity weakens for three rules**, per the Established facts section.

## What was not investigated

Named so the reader can tell which parts rest on assumption.

- `src/humansays/const.py` was not read in full. Exit-code values and
  `SEVERITY_ORDER` are referenced by name only. Task 6 touches `CLI_DESTINATIONS`
  there and must read it first.
- `docs/site/planned/index.md` was not read. The `hint` and `evidence`
  definitions used here are quoted secondhand from `reconciliation.md:11-17`.
  Read the primary source before writing `docs/site/output.md` in Task 7.
- `tests/integration/test_cli_contract.py` was not read in full; its tests are
  class-based, so a `def test_` grep undercounts them. Read it before Task 6.
- The interaction between `--fail-on` / `--min-score` and a score that can now
  reach 100 with findings present was **not analyzed at all**. A repository
  whose only findings are hints will pass `--min-score 90` while printing
  findings. That may be correct; it has not been checked against
  `tests/integration/test_exit_contract.py`. Resolve it in Task 5.

## Out of scope

Evidence citation; the review profile; profile-based rule selection; the 10
`evidence` demotions; the 3 splits; identifier renames; per-rule enable/disable
in `humansays.toml`; path-scoped rule activation; retiring `SignalName`;
pruning evaluation work for disabled rules.

If a step cannot be completed as written, stop and report. Do not substitute an
approach.

## Discovered during execution

<!-- Per agent-protocol.md §4b this section is the highest value-per-line part
     of the plan for the next phase's author: it records what the tree turned
     out to be, not what this plan assumed. -->

- **Half the byte-diff corpus produces no findings at all.** `.migration/
  capture.sh` scans two corpora, `poc` and `django`. Measured during Task 3:
  `poc` is 14 files and **0 signals**, score 100.0. Every `poc` capture — text
  and JSON, colour both ways, four of the eight files compared — is an empty
  finding list, and comparing two empty lists always matches.

  This is retroactive about C1. That phase's headline gate was an empty byte
  diff reported `IDENTICAL` at all seven commits; half of what it compared was
  empty output, and the real evidence was 3 files and 9 findings in `django`.
  The gate was not wrong, it was **half as strong as it read**, which is the
  §4c failure mode exactly: a gate whose blind spot was never written down.

  The reason `poc` is clean is legitimate — it is the prototype's own source,
  and the prototype's 20 self-findings were all comment- and docstring-counting,
  which humansays retired as HS010 and HS011. So the corpus is not broken; it is
  just not evidence. Widening it is filed in `.agent-specs/backlog.md`; C2 does
  not widen it, and the before/after table below is honest about resting on
  `django` alone.

- **HS015 fires in none of the available corpora.** Measured: `django` fires
  HS016 and HS021; `poc` fires neither; `src/humansays` fires only HS005 and
  HS002. So of the three rules C2 demotes, **only two have any observable
  effect on any captured score**. HS015's demotion is verified by its frozen
  metadata and by a fixture test, and by nothing in the before/after table. Say
  so in the table rather than presenting three demotions with two rows of
  evidence.

- **Tasks 3 and 4 merged.** The plan put the scoring filter in `scoring.py`.
  It went on `RuleSpec.penalty` instead, which returns `0.0` for anything that
  is not `ON`. `scoring.py` already sums `finding.rule.penalty`, so the filter
  is single-sourced at the definition of penalty rather than at one of its
  callers, and the finding still reaches the report to be displayed — which was
  Task 4's actual requirement. Nothing else sums penalties today, but if
  anything ever does, it inherits the rule instead of having to remember it.

- **`--fail-on` had to change, and the plan had listed it as uninvestigated.**
  `application.py:169` keyed the exit code on `Severity` alone. Since the score
  already ignores anything that is not `ON`, leaving it there would let
  `--fail-on warning` and `--min-score` disagree about the same run: `HS016` is
  a `hint` whose severity is still `WARNING`, so a file of nothing but lambdas
  would score 100 and still fail the build. `severity_exit` now counts only
  scored findings. A hint that fails your build is not a hint.

- **The self-scan caught the new code, which is the first time that constraint
  has fired.** `*, show_evidence: bool` in `reporting/grouping.py` is HS002
  boolean-modes — the same false positive already baselined twice for `_style`
  and `indicator_text`, caused by `declared_arguments()` merging posonly,
  positional and keyword-only. Two baseline entries added with that reason and
  the existing `phase-2-argument-kind-fix` expiry. Restructuring working code
  to dodge a known documented false positive would have been the worse trade,
  and the baseline exists for exactly this.

- **The self-scan baseline is unaffected by the demotion, measured rather than
  reasoned.**
  `src/humansays` fires only HS005 and HS002, neither of which C2 touches, so
  `test_self_scan_matches_baseline_exactly` needs no baseline edit. This was
  flagged in Task 5 as "probably untouched, must be run not reasoned about" —
  it was run.
