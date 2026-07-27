# Evaluation model

**Revision note.** This supersedes an earlier draft that used a single
`defect / inspect / observation` tier, a computed 0–20 scalar score, and a
multiplicative confidence formula. All three were wrong for reasons recorded in
[`../evidence/critique-log.md`](../evidence/critique-log.md). Do not reintroduce
them.

---

## 1. Claims and evidence are separate axes

The earlier draft collapsed "how serious is this claim" and "how sure are we"
into one enum. That forced every rule to lie about one to express the other,
which is how a sectioning comment ended up labelled a defect.

Two independent attributes on every rule:

### 1.1 Claim type — what kind of assertion is being made

| Claim | Meaning | Examples |
|---|---|---|
| `bug` | Known incorrect behavior or a language hazard | mutable default argument, `return` inside `finally` |
| `risk` | Structure that is failure-prone, though possibly intentional | broad exception swallowed, module-global write |
| `design` | Maintainability, responsibility or clarity concern | positional boolean, zero-state namespace class |

### 1.2 Fact certainty — was the condition observed or inferred

| Certainty | Meaning |
|---|---|
| `observed` | Directly present in the fact model; no interpretation |
| `derived` | One inference step from facts |
| `heuristic` | Naming-based or pattern guess |

### 1.3 Impact — how consequential the likely problem is

**Deliberately unassigned until Phase 5.** Hand-assigning `high`/`medium`/`low`
is the unjustified-constant error the critique log records twice, wearing a nicer
name. `impact` is derived from repair correspondence in the paired before/after
corpus: a rule whose findings are routinely repaired has demonstrated impact.

No profile may use `impact` until it is populated from measurement.

### 1.4 Report role — may this appear alone

`standalone` or `evidence`. An `evidence` rule is correlation input and is never
reported on its own. This was previously folded into evidence strength as
`context`, giving a fourth job to a field already doing two.

### 1.5 Why four fields

An earlier two-field draft said four arguments is `weak` evidence and nine is
`strong`. The count is equally *observed* in both cases. What differs is the
magnitude of the condition, and so the likely impact — not the certainty of the
fact.

Magnitude is carried as a numeric field on the finding and reported. Until
`impact` is populated it changes no classification.

A `bug` claim can rest on a `heuristic` fact. A `design` claim can rest on an
`observed` one. The axes never collapse.

### 1.6 Why this matters

Terminology determines trust. Once a tool calls a legitimate design choice a
"defect," its strongest word comes to mean "the author dislikes this," and the
tool becomes CI furniture. `bug` must remain rare and mean what it says.



---

## 2. Reporting, not scoring

### 2.1 What ships in the MVP

**No scalar score.** Not per unit, not per repository.

The earlier draft computed a 0–20 total from the Python criteria document's §15
scorecard. Computing a number from a rubric does not inherit the rubric's
validity, and the 0/1/2 collapse made one marginal finding indistinguishable
from ten serious ones. The aggregation was also underspecified in ways that
would have been discovered only after users depended on it — whether function
lines count inside their containing class and module, how overlapping unit spans
are handled, whether generated files and tests are weighted like production
code, which category receives a finding supported by four dimensions, and
whether a 3,000-line generated module can dominate twenty careful domain
modules.

### 2.2 What ships instead

The §15 category layout is retained as a **reporting template**, because its
legibility is a real asset and the user already thinks in those terms. It
carries concentration, not a grade:

```
State ownership
  2 risk findings (strong), 1 design finding (moderate)
  8 units affected, 11% of analysed non-test lines
  strongest evidence: shared mutable binding, server/registry.py:44

Abstraction
  2 design findings (moderate)
  2 units affected, concentrated in server/workflow.py

Failures            no findings
Testability         not analysed (no test paths configured)
```

`not analysed` is a first-class outcome and must be distinguishable from
`no findings`.

### 2.3 When a scalar may be added

Only after it is shown to predict something: reviewer acceptance, defect
density, repair success, or maintenance outcome. See
[the retired measurement roadmap](../roadmap-retirement.md) for the paired
before/after corpus that makes this testable.

Until then, any number the tool prints must be labelled uncalibrated in the
output itself, not merely in the documentation.

---

## 3. Confidence

### 3.1 Named bands with explicit reasons

```json
{
  "confidence": "medium",
  "raises_confidence": [
    "writes two distinct state owners",
    "performs filesystem I/O"
  ],
  "lowers_confidence": [
    "function name indicates orchestration"
  ]
}
```

Bands: `high`, `medium`, `low`.

### 3.2 Why not a formula

The earlier draft specified:

```
confidence = base(rule) × evidence_agreement × contradiction_penalty × certainty
```

Nothing justified multiplication over additive log-odds, nothing established
`base(rule)`, nothing defined independence, nothing prevented correlated facts
from inflating one another, and nothing validated the output. A decimal
confidence with unjustified constants is subjective judgment with multiplication
signs attached — the same error this project identified in the proof of
concept's static per-rule confidence.

### 3.3 The path to numbers

The band-plus-reasons format is deliberately the input format a calibration
would need. Once a labelled corpus exists, fit log-odds weights to the reason
lists and replace bands with probabilities that mean something. Not before.

---

## 4. Correlation requires independent evidence dimensions

### 4.1 The rule

A correlated finding fires only when facts from **at least two independent
evidence dimensions** support it. Each finding declares which dimensions must be
independent.

| Dimension | Source |
|---|---|
| `ownership` | Mutation targets, field writes, binding scope |
| `effect` | Resolved effect edges |
| `control-flow` | Nesting, branching, handler regions, path partitions |
| `naming` | Identifiers, docstrings, comments |
| `shape` | Spans, counts, clustering |
| `call-graph` | Resolved call edges, call-site counts |
| `runtime` | Observed execution facts |

### 4.2 Why not families

The earlier draft required signals from two different *families*. That is
organizational metadata, not proof of independence. `role-conflict` and
`mixed-abstraction-levels` sit in different families but can both derive from
one call sequence — the catalog agreeing with itself, not evidence agreeing.

Conversely, some single-dimension facts are conclusive on their own. A mutable
default argument needs no corroboration.

### 4.3 Consequence

Each finding definition in the rule book carries a `requires_independent`
list. A finding whose supporting signals all trace to the same dimension does
not fire, regardless of how many signals there are.

Signals that feed a finding are reported as its evidence, not separately, so a
finding and its inputs never double-count.

---

## 5. Output guards

These are **unusability guards, not accuracy measurements.** They prevent output
nobody can read. They do not indicate the tool is right.

| Guard | Threshold |
|---|---|
| Findings per KLOC, default profile | < 3 |
| Single rule share of total output | < 15% |
| Rules emitting zero findings across the whole corpus | flagged for review |

The third guard exists because a tool emitting nothing satisfies the first two
perfectly.

**A legitimately common defect may exceed 15% of output.** When that happens the
guard has found a fact about the corpus, not a bug in the rule. Investigate
before retuning.

Accuracy needs separate measurement and none of it is available at MVP:
precision per rule, reviewer dismissal rate, repair acceptance rate,
false-positive concentration, recurrence after suppression, and the proportion
of findings whose repair is behavior-preserving. These require a labelled corpus
or human raters. See [the retired measurement roadmap](../roadmap-retirement.md).

---

## 6. Selection semantics

Four orthogonal set-valued flags. No flag does two jobs.

```
--claim        bug,risk,design                  which claim types to emit
--min-certainty observed | derived | heuristic   fact-certainty floor
--include-family  HS-STATE,HS-EFFECT            additive family filter
--exclude-family  HS-NARRATION                  subtractive family filter
--evidence-source static,calibrated,observed    which fact sources may be used
```

`--evidence-source` replaces the earlier `--mode` flag, which conflated "where
facts come from" with "which findings are eligible."

### 6.1 Profiles

Profiles are named flag combinations and nothing more. Each expands to an exact
command shown by `humansays profile show <name>`.

**A profile is a reviewed set of emittable rule IDs.** Flags express that set; a
snapshot test asserts they reproduce it.

An earlier draft defined `default` as `--claim bug,risk` before the claim
distribution existed. Measured against the resulting catalog it would have
emitted **one of six** MVP findings, because five were `design` claims. The
algebra silently suppressed the majority of the work it shipped.

| Profile | Intent |
|---|---|
| `default` | Correctness and reliability: `bug` and `risk`, plus any `design` finding with demonstrated repair correspondence |
| `agent` | `default` plus narration and orchestration findings, regardless of claim type |
| `review` | Everything static, all claim types |
| `deep` | `review` plus calibrated and observed sources |
| `everything` | No filtering |

- [ ] `humansays profile show <name>` prints the flag expansion **and** the exact
      emittable rule-ID set
- [ ] A catalog-snapshot test asserts that set, reviewed on change
- [ ] If flags cannot reproduce the intended set, the flag design is wrong, not
      the set

`--claim` is a set, not a ceiling. `--evidence-source` is additive: it augments,
never replaces.

---

## 7. Where nondeterminism lives

Observed evidence is nondeterministic by construction. It never contributes to
any aggregate figure the tool prints.

The deterministic guarantee is:

> Given the same source, configuration, tool version, **and calibration artifact
> digest**, static output is byte-equivalent canonical JSON.

The artifact digest is part of that statement, not an aside. Static analysis
reads the calibration artifact when present, so source plus config plus version
is not a sufficient input set. Canonical JSON therefore carries an `inputs`
block naming every digest that affected the run. See
[`04-execution-modes.md`](04-execution-modes.md) §3.
