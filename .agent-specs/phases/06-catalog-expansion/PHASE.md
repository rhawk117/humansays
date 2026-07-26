# Phase 6 — catalog expansion

**Goal.** Expand the catalog only where the pilot and the study justify it.

**Read this file, `docs/site/rules/python.md`, `docs/evidence/` study results.**

---

## Preconditions

- [ ] Phase 4 pilot findings shipping
- [ ] Phase 5 studies complete, `impact` populated where sample permits

## Gate

A rule is eligible for implementation when **all** hold:

- [ ] It cites a criteria-document section with current zero coverage, **or** it
      supports a finding whose pilot demonstrated repair correspondence
- [ ] Its family's pilot rules met the output guards on the large-repo corpora
- [ ] A positive and a matched negative microfixture can be written before the
      implementation

A rule that fails the gate is not implemented. Rule count is not a metric; the
guards are.

## Order

1. Remaining `HS-ARGS`, `HS-STATE`, `HS-CLASS` — same fact model as the pilot
2. `HS-FAIL` static subset
3. Remaining `HS-NARRATION` — subject to the Study 2 caveat that its rules stand
   on repair correspondence, not on authorship
4. Remaining findings whose dimensions are satisfiable statically

Effect-dependent and runtime-dependent rules stay deferred to Phases 7 and 8.

## Acceptance criteria

- [ ] Every added rule passed the gate, with the gate decision recorded
- [ ] Output guards **re-derived** for the resulting claim distribution, not
      inherited
- [ ] Catalog-snapshot test updated; every profile's emittable set reviewed
- [ ] Criteria-coverage report shows which sections remain uncovered

## What a wrong implementation looks like

1. **Rules added because they were easy**, not because the gate passed.
2. **Guards inherited rather than re-derived** after the distribution changed.
3. **The profile snapshot was regenerated without review**, hiding a suppression
   regression.
4. **`HS-NARRATION` expanded on the authorship premise** rather than on repair
   correspondence.
