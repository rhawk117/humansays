# Idea register

Feasibility 1–5 (5 = prototyped). Value 1–5 (5 = differentiating).
Effort S/M/L/XL.

| Idea | Feas | Value | Effort | Verdict |
|---|:--:|:--:|:--:|---|
| Argument-kind split | 5 | 5 | S | Prototyped; fixes a proven correctness bug |
| Delete `PY010`/`PY011` | 5 | 4 | S | Done. Measured: 26% faster, 61% quieter, identical score |
| Drop `pydantic-settings` | 5 | 5 | S | Done. Measured 204 ms |
| Claim/evidence split | 5 | 5 | S | Keeps `bug` meaningful |
| Scorecard as reporting template | 4 | 4 | M | Layout without a scalar |
| Confidence bands with reasons | 5 | 4 | S | Honest, and it is the input format a calibration would need |
| Evidence-dimension independence | 4 | 5 | M | Fixes the two-families hole |
| Microfixture pairs | 5 | 5 | M | Positive plus matched negative per rule |
| Paired before/after corpus | 4 | 5 | L | The only measurement that tests the product's actual claim |
| Matched-pair narration study | 4 | 4 | M | Gates twelve rules |
| Large-repo volume guards | 5 | 3 | S | Unusability guard, not accuracy |
| Scalar score | 2 | 3 | M | **Deferred.** Only after it predicts something measurable |
| Audit-event vocabulary | 5 | 4 | S | Verified. Hedge the completeness claim |
| Import-edge classification | 5 | 4 | S | Extractor exists, consumer is wrong |
| Bytecode dependency summarizer | 4 | 5 | L | Prototyped end to end |
| First-party call graph | 3 | 4 | XL | Only if the effect gate demands it. 13x slowdown |
| Audit-hook calibration | 5 | 5 | M | Turns "is my effect model right" into a number |
| Per-call-site coverage partitioning | 4 | 5 | M | Strongest evidence form available; nothing else does this |
| Branch-never-taken | 4 | 5 | S | Highest-volume real defect in generated code |
| Identity-stable parameters | 4 | 4 | S | Implements criteria §3 with proof |
| Observed handler narrowing | 4 | 4 | S | Turns a style nag into a mechanical refactor |
| Instance-growth detection | 4 | 4 | M | Verified via `WeakSet` |
| Project-type cycle detection | 4 | 3 | M | Report as finalization delay, not leak |
| `ResourceWarning` capture | 5 | 3 | S | Nearly free |
| `tracemalloc` attribution | 4 | 3 | M | Good diagnostics, weak as a rule |
| Process pool over files | 5 | 4 | S | Zero cross-file state |
| Content-hash cache | 4 | 4 | M | After the schema freezes |
| Rust dependency summarizer | 4 | 4 | L | Best first Rust target; safe to learn on |
| Rust standalone binary | 3 | 5 | XL | Post-1.0. The only path to grammar independence |
| PyO3 node-level extension | 2 | 1 | L | **Do not build.** FFI on the hottest call site |
| Second `LanguagePack` stub | 5 | 4 | S | Validates the contract for the price of a toy |
| Language-neutral fact schema | 2 | 1 | L | **Rejected.** The overlap is near-empty |
| Four-field taxonomy (claim/certainty/impact/report) | 5 | 5 | S | Replaces the two-field scheme |
| Impact derived from repair correspondence | 4 | 4 | M | Never hand-assigned |
| Profile-as-emittable-ID-set + snapshot test | 5 | 5 | S | Catches the suppression bug mechanically |
| Effect gate on precision + recall | 4 | 5 | M | Volume alone is not correctness |
| `sitecustomize` instrumentation bootstrap | 3 | 4 | M | Subprocess propagation is unsolved otherwise |
| Single severity tier | 1 | 1 | S | **Rejected.** See `evidence/critique-log.md` §1 |
| Multiplicative confidence formula | 1 | 1 | S | **Rejected.** See `evidence/critique-log.md` §3 |
| Family-based correlation | 2 | 2 | S | **Rejected.** Families are metadata, not independence |
| Hand-assigned impact | 1 | 1 | S | **Rejected.** See `evidence/critique-log.md` §15 |
| Volume-based effect gate | 1 | 1 | S | **Rejected.** See `evidence/critique-log.md` §20 |
| Bash scope guard | 1 | 1 | S | **Rejected.** Enforced nothing; see §13 |

These are scored ideas, not scheduled work. Nothing here is planned, nobody is
assigned, and an entry sitting here for a year costs nothing. If one is worth
doing, it gets a plan under [`../plans/`](../plans/) and stops being an entry
here.
