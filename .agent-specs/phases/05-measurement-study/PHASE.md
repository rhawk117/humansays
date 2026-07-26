# Phase 5 — measurement study

**Goal.** Run the studies the Phase 3 harness was built for, against the real
detectors from Phase 4.

**Read this file and `.agent-specs/design/02-evaluation-model.md`.**

---

## Preconditions

- [ ] Phase 3 harness complete, corpus collected
- [ ] Phase 4 pilot findings implemented in production code

**Use the production detectors.** Do not build experimental duplicates under
`scripts/` — two implementations of the same semantics will disagree, and you
will trust the wrong one.

---

## Study 1 — repair direction

For each before/after pair in the corpus:

- [ ] The finding that motivated the repair is present in *before* and absent in
      *after*
- [ ] No **new** finding appears in *after* **in the same review category**

The second condition is stated by category, not by severity ordering. `bug`,
`risk` and `design` are claim *types*, not an ordered scale — "no equal-or-
greater claim" is undefined and must not be used.

Report per rule: how often its findings correspond to accepted repairs. **This
is the derivation of `impact`.** A rule whose findings are routinely repaired has
demonstrated impact; one whose findings are routinely left alone has not.

- [ ] Populate `impact` in the catalog from this result, with the sample size
      recorded per rule
- [ ] Rules with insufficient sample keep `impact: unassigned`. Do not guess

## Study 2 — narration prevalence

**This study gates nothing about claim or certainty.**

An earlier design tiered `HS-NARRATION` on the assumption that generated code has
higher incidence, and treated a null result as requiring twelve rules to be
re-tiered. That was wrong: authorship prevalence is a positioning result, not a
validity result. Whether sectioning comments are more common in generated code
tells you nothing about whether they indicate poor structure, whether repairing
them improves code, or what the rule's claim should be. Those questions are
answered by Study 1.

If claim or certainty assignments would change based on this study's outcome, the
catalog is contaminated by an authorship assumption the tool has promised not to
make. Fix the catalog, not the study.

### Design

Matched pairs: the **same task**, implemented once by a human and once by a
model, with **equivalent context on both sides**.

- 30 tasks minimum
- Both sides receive the same task context: repository state, surrounding code,
  tests, and constraints. Docstring-only versus full repository context is not
  matched
- **Multiple generations per task** — one sample per task measures sampling
  noise wearing a confidence interval. Five minimum
- Report per-rule incidence difference with a confidence interval and the
  generation count

### Outcome

| Result | Action |
|---|---|
| Clear difference | Record it in `docs/evidence/narration-study.md`. It may be used in positioning |
| No difference | Record it. The rules stand on Study 1. Remove any documentation implying a generated-code association |
| Higher in human code | Record it. Still no change to claim or certainty |

**In no case does the tool output text asserting that code was generated.**

## Acceptance criteria

- [ ] Study 1 run against production detectors; per-rule repair correspondence
      recorded
- [ ] `impact` populated where sample size permits, `unassigned` elsewhere, with
      sample sizes recorded
- [ ] Study 2 run with matched context and ≥5 generations per task
- [ ] `docs/evidence/narration-study.md` written, including a null result if
      that is the outcome
- [ ] No claim or certainty value changed as a consequence of Study 2

## What a wrong implementation looks like

1. **Duplicate detectors built under `scripts/`.** Calibration and production
   disagree; you trust the wrong one.
2. **`impact` assigned where sample size was thin.** A new unjustified constant.
3. **Study 2 used unmatched context** — full repository for the human, docstring
   for the model.
4. **One generation per task.** Sampling noise with error bars.
5. **A claim value changed because Study 2 came back null.** The catalog was
   contaminated; that is the finding.
