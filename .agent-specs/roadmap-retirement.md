# Roadmap retirement

The retired phase tree defined a nine-phase sequence built around the
rule model that predated the current catalog. That catalog now lives at
`docs/site/planned/` as 175 rules across fifteen domains, and the project
plans only the next piece of work rather than a multi-phase sequence in advance.
This file records, phase by phase, whether each phase's premise still holds
against the current catalog. It is the permanent record. The phase directories
have been deleted. Work that remains worth doing moves to `backlog.md` as an
unordered list.

Classification is by catalog alignment, not by completion. "Misaligned" means
the phase's premise or scope was built around the old rule model and no longer
makes sense as written. "Still worth doing" means the goal is independent of
which catalog is in effect.

## 01-review: misaligned

Stated goal: reconcile the `feat/proof-of-concept` build against the
specifications that postdate it, repair the scope guard, and reserve the PyPI
name.

Reconciliation is the phase's core, and it is bound to the superseded state.
The `HS###` identifiers, the `PY010`/`PY011`/`PY020` deletions, the parity
oracle against `.poc-reference/`, and the self-scan baseline all describe the
proof-of-concept build measured against the old single-page catalog and criteria
document. None of those artifacts define the current catalog. The per-phase
scope guard (`allowed-paths.txt`, `scripts/check_scope.py`) served the
phase-isolation discipline that this branch retires. The only catalog-independent
element, the release pipeline and PyPI name reservation, is already realized:
`.github/workflows/release.yml` exists and `0.1.0a1` shipped. Nothing here
carries to the backlog.

## 02-fact-model: still worth doing

Stated goal: make the fact model capable of expressing argument kinds, claim and
certainty, and immutable facts.

The fact-model capabilities are infrastructure that any catalog needs. The
current catalog still separates operation inputs from configuration
(`CONTRACT003`, `CONTRACT004`), still needs frozen facts so rule evaluation
cannot mutate shared state, still needs canonical parser-independent
serialization for a future reimplementation, and its config already carries
path-scoped selection through `per-file-ignores`. Those pieces survive. One task
does not: migrating rules to the old `bug|risk|design` severity columns of
the old `docs/site/rules/python.md`. That page is gone, and the current model
defines its own claim, concern, certainty, and default fields on the published
pages. The
claim-migration task is misaligned; the rest of the phase is not.

## 03-measurement-harness: still worth doing

Stated goal: build the measurement instrument across four corpus types, running
no studies.

Every part is catalog-independent. Matched positive and negative microfixtures
per rule, before/after repair pairs from real accepted fixes, large-repo corpora
carrying output-volume and concentration guards rather than score assertions,
and a repair-direction harness apply to any rule set. The standing project
constraint already requires a positive and a matched negative microfixture per
rule, so the harness that enforces it is directly useful.

## 04-pilot-rules: still worth doing

Stated goal: implement three vertical findings end to end, with independence
tests and profiles defined as emittable ID sets.

The "exactly three, then measure before expanding" scoping is an artifact of the
retired sequence and no longer applies now that the catalog is already large.
The methodology under it survives and is catalog-independent: correlated findings
declaring required-independent dimensions and proving by test that they do not
fire when all supporting signals trace to one dimension, supporting signals
reported as evidence rather than as standalone findings (the current `evidence`
default), and profiles defined as an expected emittable-rule-ID set with a
snapshot test before the selection flags are written. The three named findings
themselves exist in the current catalog as `ENCAP011`, `KISS004`, and `SMELL014`.

## 05-measurement-study: still worth doing

Stated goal: run the repair-direction and narration-prevalence studies against
real detectors.

The repair-direction study measures whether a rule's findings correspond to
accepted before/after repairs. That is the product's central claim and is
independent of the catalog. The narration-prevalence study, run with matched
human and model context and several generations per task, is also
catalog-independent, and its constraint that no claim or certainty value may
change on its outcome matches the standing rule that authorship is not observable
from structure. The one detail tied to the old model is the `impact` field the
study was meant to populate. The current model scores through domain `weight` and
per-rule `default`, with no `impact` field, so the survivor is the measurement
itself, framed as per-rule repair correspondence, not the old field.

## 06-catalog-expansion: misaligned

Stated goal: expand the catalog from the three pilot rules toward the remaining
signals, in a fixed order, gated by study results.

The premise is that a small pilot catalog grows outward under study-driven gates.
The current catalog already contains 175 rules across fifteen domains, built
without this sequence. Expanding from three pilot rules in the order this phase
specifies describes work that is already done differently. The eligibility bar it
defined, that a rule cites a criteria section, ships with matched fixtures, and
meets output guards, survives through the standing citation rule and the Phase 3
fixtures rather than through this phase.

## 07-effects: still worth doing

Stated goal: make effect classification work on real code through audit-event
vocabulary, import-edge classification, bytecode summarization, and a first-party
call graph, stopping when measurement allows.

Effect classification is infrastructure the current catalog depends on directly.
Rules such as `SOLID001`, `KISS001`, the `POLA` effectful-property and operator
rules, and the `err.effect_*` evidence facts all require knowing what a call
does. The layered approach and its two hard constraints, never importing
third-party code to analyze it and never running the summarizer on the scan path,
match the standing project rules. The correctness gate, which checks recall
against fixtures plus a bounded manual precision sample and stops at the earliest
passing layer, is catalog-independent.

## 08-dynamic: still worth doing

Stated goal: add runtime evidence through a calibration artifact and an
observation mode, without breaking determinism or the scan budget.

The current catalog ships `observe`-default rules (`CONC007`, `LIFE004`,
`LIFE005`, `LIFE006`, `SMELL006`), so the observation machinery is required to make
them real. The separation the phase enforces, that observed evidence never enters
an aggregate, is the standing project rule on nondeterministic evidence.
Content-addressed calibration artifacts, complete environment fingerprints,
warn-and-refuse staleness, and per-finding provenance including call-site
coverage are all catalog-independent.

## 09-performance: still worth doing

Stated goal: exhaust pure-Python optimization headroom, then decide on Rust from
evidence.

Nothing in this phase depends on the catalog. Single-traversal extraction,
evaluating only enabled rules, parallel per-file analysis that produces
byte-identical output to serial, a content-hash cache after the fact schema
stabilizes, and an evidence-gated Rust decision are all about scan speed and the
fact pipeline. It survives whole.

---

Two phases are misaligned (01-review, 06-catalog-expansion). Seven are still
worth doing (02, 03, 04, 05, 07, 08, 09).
