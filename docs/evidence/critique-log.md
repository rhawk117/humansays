# Critique log

**Round 1** entries 1–12. **Round 2** entries 13–22, from an external review
that tested claims rather than reading them. Two round-2 findings were verified
empirically before acceptance.

Ideas that were proposed, found wrong, and replaced. Recorded rather than
deleted so they are not reintroduced.

If you find yourself proposing one of these, read the entry first.

---

## 1. Single severity tier (`defect` / `inspect` / `observation`)

**Wrong because** it collapsed two independent axes — how serious the claim is,
and how well supported it is — into one enum. That forced rules to misrepresent
one to express the other. Sectioning comments, positional booleans, stateless
one-method classes and mutable `ClassVar` collections were all labelled
`defect`, which does not mean "behavior is wrong."

Terminology determines trust. Once the strongest word means "the author dislikes
this," the tool becomes CI furniture.

**Replaced by** `claim` (`bug`/`risk`/`design`) and `evidence`
(`strong`/`moderate`/`weak`/`context`) as independent attributes. Under the
stricter definition, `bug` went from ~32 rules to 3.

---

## 2. Computed 0–20 scorecard total

**Wrong because** computing a number from a rubric does not inherit the rubric's
validity. The 0/1/2 collapse made one marginal finding indistinguishable from
ten serious ones, while a unit with twenty observations and one inspection could
score maximum. Aggregation was underspecified: whether function lines count
inside their containing class and module, overlapping unit spans, generated
files, test weighting, non-applicable categories, whether a 3,000-line generated
module can dominate twenty domain modules, which category receives a
multi-dimension finding, and whether findings double-count their supporting
signals.

**Replaced by** the §15 category layout as a **reporting template** carrying
concentration, with no scalar. A scalar may be added only after it is shown to
predict reviewer acceptance, defect density, repair success or maintenance
outcome.

---

## 3. Multiplicative confidence formula

```
confidence = base(rule) × evidence_agreement × contradiction_penalty × certainty
```

**Wrong because** nothing justified multiplication over additive log-odds,
nothing established `base(rule)`, nothing defined independence, nothing
prevented correlated facts from inflating one another, and nothing validated the
output. Decimal confidence with unjustified constants is subjective judgment
with multiplication signs attached — the same error identified in the proof of
concept's static per-rule confidence.

**Replaced by** named bands (`high`/`medium`/`low`) with explicit
`raises_confidence` and `lowers_confidence` reason lists — which is also the
input format a real calibration would need.

---

## 4. Correlation across two *families*

**Wrong because** families are organizational metadata, not proof of
independence. `role-conflict` and `mixed-abstraction-levels` sit in different
families but can both derive from one call sequence: the catalog agreeing with
itself. Conversely a single-family fact like a mutable default argument is
conclusive alone.

**Replaced by** independence across **evidence dimensions** (`ownership`,
`effect`, `control-flow`, `naming`, `shape`, `call-graph`, `runtime`), with each
finding declaring which must be independent.

---

## 5. `HS-LLM` family name

**Wrong because** the tool detects narrative structure; it cannot infer
authorship from structure. Sectioning comments occur legitimately in compiler
passes, cryptographic routines, migration scripts, parsers, numerical
procedures, educational implementations and linear orchestration code.

The proposed validation — generated code versus Django — also confounds
authorship with framework, age, contributor count, style and domain.

**Replaced by** `HS-NARRATION`, plus a matched-pair study (same task,
human-authored and model-authored) in Phase 3.

---

## 6. Single calibration corpus with a minimum score

**Wrong because** Django, `requests` and CPython `Lib/` are regression corpora,
not exemplars of clean architecture. They deliberately contain registries,
global state, import-time behavior, compatibility branches, monkeypatching,
broad exception boundaries and namespace classes. A minimum-score assertion
forces either bending the rules until Django passes, or treating Django's
compromises as universal good practice.

**Replaced by** four corpus types: positive microfixtures, matched negative
microfixtures, paired before/after accepted repairs, and large repositories used
for volume and concentration only.

---

## 7. Output budgets presented as precision

**Wrong because** volume constraints do not prove accuracy. A tool emitting
nothing satisfies them perfectly, and a legitimately common defect may exceed a
15% share.

**Replaced by** the same thresholds, relabelled as **unusability guards**, plus
a third guard for rules that never fire, plus a documented list of the accuracy
measurements that actually matter and are not yet available.

---

## 8. Committed `.humansays/observed.json` by default

**Wrong because** a runtime artifact can carry absolute paths, module structure,
test-only behavior, exception types, coverage, execution counts,
environment-specific branches, private package names and test-data
characteristics. It also churns on merge and goes stale invisibly.

It also created a **determinism contradiction**: static output was claimed
deterministic given source, config and version, while static analysis reads the
artifact when present.

**Replaced by** a local content-addressed cache as the default, CI artifact for
pull requests, opt-in sanitized committed baseline, a complete fingerprint,
warn-and-refuse on mismatch, and the artifact digest as a declared input in
canonical JSON.

---

## 9. Audit events as a complete effect enumeration

**Wrong because** third-party native extensions may expose different or no
events, in-memory mutation is an effect without being external I/O, some events
(`compile`, `exec`) are not ordinary outside-world interaction, and an event
names an operation rather than its architectural meaning.

**Replaced by** the hedged wording in `design/03-effect-architecture.md`.

---

## 10. Dependency cache keyed on the lockfile hash

**Wrong because** results also depend on Python version, platform and
environment markers, selected extras, wheel versus sdist, package build,
analyzer version, bytecode dialect, effect-vocabulary version and summarizer
schema.

**Replaced by** a composite environment fingerprint.

---

## 11. "A promoted signal keeps its ID"

**Wrong because** it contradicted the accompanying rule that number ranges
distinguish signals from findings. Both could not hold.

**Replaced by** findings as distinct rules from inception in an `HS-FIND`
namespace. Promotion is not an operation. Number ranges carry no meaning.

---

## 12. `--tier` and `--mode`

**Wrong because** both did two jobs. `--tier inspect` did not say whether
defects were included; `--mode observe` did not say whether static evidence was
replaced or augmented; `default` excluded a family without saying so in its
definition.

**Replaced by** four orthogonal set-valued flags — `--claim`, `--min-evidence`,
`--include-family`/`--exclude-family`, `--evidence-source` — with every profile
expanding to an exact command shown by `humansays profile show`.


---

# Round 2

## 13. The scope guard did not enforce anything — VERIFIED BY TEST

Documented as physically blocking `signature.py` during Phase 1. **It blocked
nothing.** Reproduced: `scope ok` was returned for a committed change to the
denied file, for staged files outside every pattern, and for untracked files
outside every pattern.

Three mechanical causes:

- `git diff BASE...HEAD` sees only committed changes — the index, working tree
  and untracked files were invisible
- Comments do not subtract from an earlier glob, so the "deliberately excluded"
  note was decorative
- Bash `[[ ]]` lets `*` cross `/`, so `src/humansays/**` matched at any depth

The allowlist also permitted editing the guard script itself, and nothing
enforced the "widening must be its own commit" rule.

**Replaced by** `scripts/check_scope.py`: `!` deny patterns, all four change
sources, POSIX glob semantics, isolated-widening check, self-protection. Verified
against a seven-case test.

**Wider lesson.** The claim was written before the mechanism was tested. Every
sentence claiming enforcement now names the test that demonstrates it — see
`process/agent-protocol.md` §4a.

## 14. Phases 3 and 4 were circular

Phase 3 required fixtures and studies for rules that Phase 4 implemented. The
narration cycle was direct: Phase 4 could not implement `HS-NARRATION` until the
Phase 3 study ran, and the study needed the detectors to measure.

An agent would resolve this by building duplicate experimental detectors under
`scripts/`, producing calibration logic that disagrees with production logic.

**Replaced by** harness → pilot → study → expansion, now Phases 3–6.

## 15. The taxonomy still conflated axes

"Four arguments is `weak` evidence, nine is `strong`" — the count is equally
observed in both cases. What differs is magnitude, and so likely impact, not
certainty. The two-field claim/evidence scheme committed the same error it was
introduced to fix.

The leak surfaced downstream: Phase 3 required an accepted repair to introduce
no finding of "equal-or-greater claim type," but `bug`/`risk`/`design` were
defined as types, not an ordered scale.

**Replaced by** four fields — `claim`, `certainty`, `impact`, `report`. The
acceptance criterion is restated without ordering: no **new** finding in the
**same review category**.

**Refinement on the reviewer's proposal:** `impact` ships empty. Hand-assigning
it would be the same unjustified constant with a nicer name. It is derived from
repair correspondence in Phase 5.

## 16. Phase 4 could not emit the profile it claimed to build

Measured against the catalog: 35 signals (20 `design`, 13 `risk`, 2 `bug`) and 6
findings (5 `design`, 1 `risk`). Under `default = --claim bug,risk`, exactly one
finding — `HS-FIND-10` — could emit. The `agent` profile did not help, since it
only removed a family exclusion while keeping the claim filter, so the narration
finding it existed to deliver still could not fire.

Root cause: `default` was defined before the claim distribution existed.

**Replaced by** profiles defined as reviewed sets of emittable rule IDs, with
flags expressing the set and a catalog-snapshot test asserting they reproduce it.

## 17. Deletion measurements contradicted each other — VERIFIED BY RE-MEASUREMENT

The idea register claimed 26%; the evidence document showed 4.60 s → 3.76 s,
which is 18%; and the 3.22 s figure belonged to a set including `PY016`, which
Phase 1 does not delete.

Re-measured, best of 3: baseline 4.18 s, minus `PY010`+`PY011` 3.24 s
(**22.5%**), minus `PY016` only 3.66 s (12.7%), all three 2.82 s (32.5%).
`PY020` fires zero times on Django.

The 26% came from mixing an instrumented-harness run (5.05 s) with a clean run
(4.60 s).

**Corrected.** Absolute wall-clock drifts 4.18–5.05 s on this hardware; report
percentages against a stated baseline.

## 18. "Language-agnostic facts" contradicted the architecture

Phase 2 said facts serialize to language-agnostic JSON; the cross-language design
said a language-neutral fact schema is the wrong abstraction. Both cannot hold.

**Replaced by** "parser-independent, language-pack-specific." A Rust
implementation of the *Python* extractor must reproduce Python facts; those facts
are not universal across languages.

## 19. The narration study gated the wrong thing

Claim and certainty were tiered on the hypothesis that generated code has higher
incidence. Authorship prevalence is a positioning result, not a validity result:
it says nothing about whether sectioning comments indicate poor structure or
whether repairing them improves code.

If a null result required re-tiering twelve rules, the catalog was contaminated
by an authorship assumption the tool had promised not to make.

**Replaced by** claim and certainty deriving from repair correspondence
(Study 1). The authorship study answers a separate question and gates nothing.

The study design was also unmatched — full repository context for the human,
docstring only for the model — and one generation per task measures sampling
noise. Now: equivalent context both sides, at least five generations per task.

## 20. The effect gate measured volume, not correctness

"Fires in the hundreds rather than twice" would be satisfied by a classifier
labelling every ORM call as every category. This is rejected idea #7 recurring in
a different phase.

**Replaced by** recall against effect-positive fixtures (at least 90%), a bounded
manual precision sample (50 hits at 80%, 25 negative controls at most 10% false
positive), with volume demoted to a smoke test.

"Scan-path wall-clock unchanged" was also unrealistic and is now an explicit 5%
budget.

## 21. Standing constraints froze an accidental fact

"Exactly three rules may use `bug`" is a Phase 2 migration invariant, not a
permanent law — and it sat next to "rule count is not a metric."

**Replaced by** a justification requirement: a new `bug` claim needs a cited
language reference or a reproducible incorrect-behavior fixture.

## 22. Process contradictions

The protocol required Session A to commit a red test while also stating that the
operator owns git. The review checklist required every acceptance criterion to be
machine-verified, though some are necessarily judgements.

`docs/criteria/python.md` was referenced by the review checklist but never
shipped.

**Replaced by** operator-commits-the-red-test, a machine/reviewer split in the
checklist, and `docs/criteria/` with a placeholder README.
