# Idea register

Feasibility 1–5 (5 = prototyped). Value 1–5 (5 = differentiating).
Effort S/M/L/XL.

| Idea | Feas | Value | Effort | Verdict |
|---|:--:|:--:|:--:|---|
| Argument-kind split | 5 | 5 | S | **Phase 2, task 1.** Prototyped; fixes a proven correctness bug |
| Delete `PY010`/`PY011` | 5 | 4 | S | **Phase 1.** Measured: 26% faster, 61% quieter, identical score |
| Drop `pydantic-settings` | 5 | 5 | S | **Phase 1.** Measured 204 ms |
| Claim/evidence split | 5 | 5 | S | **Phase 2.** Keeps `bug` meaningful |
| Scorecard as reporting template | 4 | 4 | M | **Phase 2–3.** Layout without a scalar |
| Confidence bands with reasons | 5 | 4 | S | **Phase 2.** Honest, and it is the input format a calibration would need |
| Evidence-dimension independence | 4 | 5 | M | **Phase 4.** Fixes the two-families hole |
| Microfixture pairs | 5 | 5 | M | **Phase 3.** Positive plus matched negative per rule |
| Paired before/after corpus | 4 | 5 | L | **Phase 3.** The only measurement that tests the product's actual claim |
| Matched-pair narration study | 4 | 4 | M | **Phase 3.** Gates twelve rules |
| Large-repo volume guards | 5 | 3 | S | **Phase 3.** Unusability guard, not accuracy |
| Scalar score | 2 | 3 | M | **Deferred.** Only after it predicts something measurable |
| Audit-event vocabulary | 5 | 4 | S | **Phase 5 Layer 1.** Verified. Hedge the completeness claim |
| Import-edge classification | 5 | 4 | S | **Phase 5 Layer 2.** Extractor exists, consumer is wrong |
| Bytecode dependency summarizer | 4 | 5 | L | **Phase 5 Layer 3.** Prototyped end to end |
| First-party call graph | 3 | 4 | XL | **Phase 5 Layer 4, only if the gate demands it.** 13x slowdown |
| Audit-hook calibration | 5 | 5 | M | **Phase 6.** Turns "is my effect model right" into a number |
| Per-call-site coverage partitioning | 4 | 5 | M | **Phase 6.** Strongest evidence form available; nothing else does this |
| Branch-never-taken | 4 | 5 | S | **Phase 6.** Highest-volume real defect in generated code |
| Identity-stable parameters | 4 | 4 | S | **Phase 6.** Implements criteria §3 with proof |
| Observed handler narrowing | 4 | 4 | S | **Phase 6.** Turns a style nag into a mechanical refactor |
| Instance-growth detection | 4 | 4 | M | **Phase 6.** Verified via `WeakSet` |
| Project-type cycle detection | 4 | 3 | M | Phase 6. Report as finalization delay, not leak |
| `ResourceWarning` capture | 5 | 3 | S | Phase 6. Nearly free |
| `tracemalloc` attribution | 4 | 3 | M | Phase 6. Good diagnostics, weak as a rule |
| Process pool over files | 5 | 4 | S | **Phase 7.** Zero cross-file state |
| Content-hash cache | 4 | 4 | M | Phase 7, after the schema freezes |
| Rust dependency summarizer | 4 | 4 | L | **Phase 7.** Best first Rust target; safe to learn on |
| Rust standalone binary | 3 | 5 | XL | Post-1.0. The only path to grammar independence |
| PyO3 node-level extension | 2 | 1 | L | **Do not build.** FFI on the hottest call site |
| Second `LanguagePack` stub | 5 | 4 | S | Any time after Phase 4. Validates the contract for the price of a toy |
| Language-neutral fact schema | 2 | 1 | L | **Rejected.** The overlap is near-empty |
| Four-field taxonomy (claim/certainty/impact/report) | 5 | 5 | S | **Phase 2.** Replaces the two-field scheme |
| Impact derived from repair correspondence | 4 | 4 | M | **Phase 5.** Never hand-assigned |
| Profile-as-emittable-ID-set + snapshot test | 5 | 5 | S | **Phase 4.** Catches the suppression bug mechanically |
| Effect gate on precision + recall | 4 | 5 | M | **Phase 7.** Volume alone is not correctness |
| `sitecustomize` instrumentation bootstrap | 3 | 4 | M | **Phase 8.** Subprocess propagation is unsolved otherwise |
| Single severity tier | 1 | 1 | S | **Rejected.** See `evidence/critique-log.md` §1 |
| Multiplicative confidence formula | 1 | 1 | S | **Rejected.** See `evidence/critique-log.md` §3 |
| Family-based correlation | 2 | 2 | S | **Rejected.** Families are metadata, not independence |
| Hand-assigned impact | 1 | 1 | S | **Rejected.** See `evidence/critique-log.md` §15 |
| Volume-based effect gate | 1 | 1 | S | **Rejected.** See `evidence/critique-log.md` §20 |
| Bash scope guard | 1 | 1 | S | **Rejected.** Enforced nothing; see §13 |
