# Phase 4 — pilot rules

**Goal.** Implement **three vertical findings** end to end, with matched
fixtures, so the measurement study in Phase 5 has real detectors to measure.

Not thirty signals. Three findings and the signals they need.

**Read this file, `docs/rules/python.md`, `docs/rules/README.md`.**

---

## Why three

The earlier design implemented ~35 signals and then measured them. That is
backwards: it manufactures vocabulary before anything has demonstrated that the
correlation model produces useful output. Three vertical slices prove the
machinery, and the study in Phase 5 tells you whether to expand.

## Preconditions

- [ ] Phase 2 complete: argument kinds, claim/certainty, frozen facts
- [ ] Phase 3 complete: microfixture harness enforced in CI, repair-pair corpus
      collected

## The three

| Finding | Signals it needs | Why this one |
|---|---|---|
| `HS-FIND-04` missing state owner | `HS-STATE-01/02/03/06`, `HS-ARGS-04` | All derivable from facts the proof of concept already extracts. Exercises `own` + `shp` independence |
| `HS-FIND-06` control-flow pressure | `HS-SHAPE-01/02/03/04`, `HS-ARGS-01` | Exercises magnitude handling and `cf` + `shp` independence |
| `HS-FIND-14` compensating commentary | `HS-NARRATION-01/03/05`, `HS-SHAPE-05` | Exercises `nam` + `shp` independence, and is the finding most specific to the product thesis |

Plus `HS-ARGS-02`, `HS-PURPOSE-02` and `HS-STATE-02` as standalone signals —
each is cheap, high-certainty, and gives the repair-pair study something with an
unambiguous fix.

## Requirements per finding

- [ ] Declares `requires_independent` dimensions
- [ ] Has a test proving it does **not** fire when all supporting signals trace
      to one dimension. Write this before writing the finding
- [ ] Reports supporting signals as evidence; those signals are not separately
      reported when cited
- [ ] Positive and matched negative microfixture

## Profiles

**Do not define profiles from claim types.** An earlier draft set
`default = --claim bug,risk`, which measured against the catalog would have
emitted one of six findings — the profile algebra silently suppressed the
majority of the work it was shipping.

- [ ] Define each profile as an expected set of emittable rule IDs
- [ ] Add a catalog-snapshot test asserting exactly which IDs each profile emits
- [ ] Express the flags afterwards, and assert the flags reproduce the snapshot

If flags cannot reproduce the intended set, the flag design is wrong, not the
intended set.

## Acceptance criteria

- [ ] Three findings implemented, each with an independence test
- [ ] Every shipped rule has positive and negative microfixtures, enforced
- [ ] Every shipped rule cites a criteria-document section, enforced
- [ ] Catalog-snapshot test exists and passes for every profile
- [ ] `humansays profile show <name>` prints both the flags and the emittable ID
      set
- [ ] Self-scan runs clean or has a reviewed baseline with reasons and expiries

## Non-goals

- The remaining ~110 signals — Phase 6, and only where the study justifies them
- Effects, dynamic analysis, cross-file work
- Any scalar score
- Populating `impact` — that is derived in Phase 5

## What a wrong implementation looks like

1. **More than three findings shipped.** The point is a pilot.
2. **A finding fires from one dimension.** Independence declared, not enforced.
3. **Profiles defined from claim types**, reproducing the suppression bug.
4. **`impact` values were assigned by hand.** They are derived from repair pairs
   in Phase 5, or they stay empty.
5. **A rule shipped with only a positive fixture.** It has not been shown to
   discriminate.
