# Phases

A phase is the execution unit. One session works one phase.

| Phase | Goal | Gate to enter |
|---|---|---|
| [01-review](01-review/PHASE.md) | Reconcile the built migration against the specs that postdate it | PR open on `feat/proof-of-concept` |
| [02-fact-model](02-fact-model/PHASE.md) | Argument kinds, claim/certainty, immutable facts | Review dispositions recorded |
| [03-measurement-harness](03-measurement-harness/PHASE.md) | Corpus format, harness, pinning, extraction tooling | Fact model stable |
| [04-pilot-rules](04-pilot-rules/PHASE.md) | Three vertical findings, end to end | Harness in CI |
| [05-measurement-study](05-measurement-study/PHASE.md) | Repair-pair evaluation, narration study, derive `impact` | Pilot findings shipping |
| [06-catalog-expansion](06-catalog-expansion/PHASE.md) | Expand only where the pilot and study justify it | Studies complete |
| [07-effects](07-effects/PHASE.md) | Effect architecture, layers 1–4 | Catalog stable |
| [08-dynamic](08-dynamic/PHASE.md) | Calibration artifact and observed findings | Effect gate passed or cut |
| [09-performance](09-performance/PHASE.md) | Python optimization, then the Rust decision | Everything above stable |

## Why 3/4/5/6 are split this way

An earlier design had measurement (3) before rules (4), which was circular:
measurement required fixtures and studies for rules that only existed in the
next phase. An agent resolving that cycle would build duplicate detectors under
`scripts/`, leaving calibration logic that disagrees with production logic.

The split is **harness → pilot → study → expansion**. Phase 3 builds the
instrument, Phase 4 builds three real detectors, Phase 5 measures them, Phase 6
expands on the result.

## Structure of a phase directory

```
PHASE.md            goal, preconditions, tasks, acceptance, non-goals,
                    and what a wrong implementation looks like
paths.json          scope guard input; {"allowed": [...], "deny": [...]}
```

## Rules

1. Read only your phase's `PHASE.md` and the reference documents it names.
2. Non-goals are load-bearing. Good work outside scope is a defect in this phase.
3. `python3 scripts/check_scope.py <phase>` must pass before review.
4. The review pass starts from **"What a wrong implementation looks like."**

## Widening a scope

Allowed, in a commit containing only the allowlist change, with a reason. The
guard enforces the isolation.
