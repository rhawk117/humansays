# Rule book conventions

## Adding or changing a rule

1. **Cite a criteria-document section.** No rule ships without one. CI enforces.
2. **Assign claim and evidence independently.** See
   `../design/02-evaluation-model.md` §1. Do not reach for `bug` — three rules
   carry it and that is close to correct.
3. **Write a positive microfixture and a matched negative microfixture.** A rule
   with only a positive fixture has not been shown to discriminate.
4. **Declare the evidence dimension.** Used for finding independence.
5. **Update the catalog and this document together.** A test asserts they agree.

## Claim assignment

| Ask | If yes |
|---|---|
| Will this code behave incorrectly, or is it a documented language hazard? | `bug` |
| Is this structure failure-prone, though possibly intentional? | `risk` |
| Is this a maintainability, responsibility or clarity concern? | `design` |

If you are unsure between `risk` and `design`, choose `design`. The cost of
under-claiming is a missed finding; the cost of over-claiming is the tool's
vocabulary losing meaning.

## Evidence assignment

| Strength | Test |
|---|---|
| `strong` | Directly present in the fact model; no interpretation |
| `moderate` | One inference step from facts |
| `weak` | Heuristic, naming-based, or at a threshold edge |
| `context` | Never reported alone; correlation input only |

Where a rule has magnitude, compute strength from it rather than creating
separate rules.

## Findings

Findings are **not** promoted signals. They are separate correlation rules in
the `HS-FIND` namespace, created as findings from the start.

Each declares `requires_independent` — the evidence dimensions that must be
independently satisfied. Write the test proving the finding does not fire on
single-dimension evidence **before** writing the finding.

Findings report their supporting signals as evidence. Signals cited by a finding
are not additionally reported on their own.

## What not to do

- Do not add a rule because it is easy to detect. Add it because a criteria
  section calls for it.
- Do not tune a threshold to make a corpus pass. The corpus is an instrument.
- Do not describe narration signals as detecting generated code.
- Do not let rule count become a metric.
