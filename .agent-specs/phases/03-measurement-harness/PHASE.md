# Phase 3 — measurement harness

**Goal.** Build the measurement instrument. **Run no studies in this phase.**

This is stage A of a split that resolves a dependency cycle: the earlier
single-phase design required fixtures and studies for rules that were only
implemented in the next phase. Sequence is now
3 harness → 4 pilot rules → 5 study → 6 expansion. Do not try to run a study
here; you would have to build duplicate detectors under `scripts/`, and you
would end up with calibration logic that disagrees with production logic.

**Read this file and `.agent-specs/design/02-evaluation-model.md`. Nothing else.**

This phase exists before Phase 4 because otherwise every rule added there makes
output noisier with no way to notice.

---

## Why the earlier single-corpus design was wrong

The earlier draft pinned Django, `requests` and CPython `Lib/` and asserted a
minimum score. Those are useful regression corpora but they are not exemplars of
clean architecture. They deliberately contain registries, global state,
import-time behavior, compatibility branches, monkeypatching, broad exception
boundaries, namespace classes, platform-specific control flow and unusual
metaprogramming.

Asserting a minimum score against them risks one of two failures: the rules bend
until Django passes, or Django's architectural compromises become the definition
of good practice.

---

## Four corpus types

### 1. Positive microfixtures

One known defect, minimal unrelated structure. One per rule, minimum.

```
tests/corpus/positive/HS-STATE-02/mutable_default.py
```

### 2. Negative microfixtures

A closely matched legitimate counterexample for the same rule. This is the part
that catches over-firing.

```
tests/corpus/negative/HS-STATE-02/frozen_default.py
```

**Every rule ships with both.** A rule with no negative fixture has not been
shown to discriminate.

### 3. Paired before/after patches

Real accepted refactors and bug fixes: the code before an accepted review fix,
and after.

**This is the most important corpus and the only one that tests the product's
actual claim** — that findings correspond to changes worth making. The assertion
is that the tool scores the accepted repair better *for the right reason*: the
finding that motivated the fix disappears, and no new finding of equal or
greater claim type appears.

Source: any repository where a review comment is followed by a fix commit.
Extraction is scriptable. Target 50 pairs for the MVP.

### 4. Large repositories

Django, `requests`, CPython `Lib/`, pinned at fixed revisions. These measure
noise, performance, concentration and ecosystem behavior. **They do not carry a
minimum score assertion.** They carry:

- output volume guards (`.agent-specs/design/02-evaluation-model.md` §5)
- concentration: no rule over 15% of output
- stability: rule changes must not move output volume beyond tolerance without
  an explicit changelog entry
- scan wall-clock

---

## What this phase does not do

- Run the repair-pair evaluation (Phase 5)
- Run the narration study (Phase 5)
- Assert per-rule fixture coverage for rules that do not exist yet


## Acceptance criteria

- [ ] Microfixture directory layout and harness exist; the harness asserts
      fire/no-fire given a rule ID and a fixture pair
- [ ] A CI check fails when a rule ships **without** both fixtures — enforced
      for whatever rules exist at the time, not for rules that do not
- [ ] ≥50 before/after pairs collected by an automated extraction script,
      committed as data
- [ ] Repair-direction harness exists and is runnable, with a passing
      self-test on synthetic input. **It is not run against real rules here**
- [ ] Large-repo corpora pinned by revision, with volume and concentration
      guards wired up (not score guards)
- [ ] Any number the tool prints is labelled uncalibrated in the output

---

## Non-goals

- New rules
- A scalar score. Not in this phase, not until §2.3 of the evaluation model is
  satisfied.
- Effect work

---

## What a wrong implementation looks like

1. **Rules were retuned until Django scored well.** The corpus is a measurement
   instrument, not a target. If Django scores badly, that is data.
2. **Negative fixtures are trivially different** from positive ones. A negative
   fixture that shares no structure with the positive proves nothing.
3. **Before/after pairs were synthesized** rather than taken from real accepted
   changes.
4. **The matched-pair study compared two corpora** instead of two
   implementations of the same task. That is the confound this task exists to
   avoid.
