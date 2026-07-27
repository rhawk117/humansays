# FAIL rules

FAIL rules examine failure boundaries, recovery strategies, retries, and rollback logic. They identify risks in partial state updates, swallowed exceptions, and unordered external effects.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| FAIL001 | Mutation between external effects | risk | hazard | on | HS-EFFECT-08 | Mutation, then effect, then mutation | `{symbol}` mutates state before and after `{effect}`, exposing a partial-state window if the effect fails. |
| FAIL002 | Unordered multi effect | risk | hazard | on | HS-EFFECT-09 | ≥2 effects with no transaction or compensation | `{symbol}` performs `{effect_count}` external effects without an observed transaction, compensation, or idempotent boundary. |
| FAIL003 | Exception leaves partial state | risk | hazard | on | HS-INIT-06 | Raise between two writes to the same owner | `{symbol}` can raise after `{completed_writes}` of `{total_writes}` writes, leaving `{owner}` partially updated. |
| FAIL004 | Broad exception swallowed | risk | hazard | on | HS-FAIL-01 | `except Exception` with `pass`/`return None` body | `{symbol}` catches `{exception}` and continues with `{fallback}`, discarding the original failure. |
| FAIL005 | Absence collapsed into failure | risk | hazard | on | HS-FAIL-05 | Infrastructure error converted to `None` return | `{symbol}` converts `{exception}` into `None`, collapsing infrastructure failure into ordinary absence. |
| FAIL006 | Retry without idempotence | risk | hazard | on | HS-FAIL-08 | Retry loop wrapping a mutating effect | `{symbol}` retries mutating effect `{effect}` without an observed idempotency key, rollback, or compensation policy. |
| FAIL007 | Error message only | design | review | on | HS-FAIL-09 | Failure distinguished by message string, not type | `{symbol}` distinguishes failure behavior by matching message text instead of an explicit exception or result contract. |
| FAIL008 | Side effect orchestration risk | risk | hazard | on | HS-FIND-02 | eff + cf | `{symbol}` coordinates `{effects}` across `{failure_regions}` failure regions without one visible recovery boundary. |
| FAIL009 | Ambiguous failure contract | risk | hazard | on | HS-FIND-12 | cf + eff | `{symbol}` exposes `{failure_modes}` failure modes through the same ambiguous return or exception contract. |
| FAIL010 | Silent infrastructure failure | risk | hazard | on | HS-FIND-13 | cf + eff | `{symbol}` suppresses `{exception}` from `{effect}`, making infrastructure failure indistinguishable from success. |
| FAIL011 | External call inside validation logic | design | review | on | Later combined catalog. | Validation reaches an external effect boundary. | `{validator}` performs `{effect}` while deciding validity, so validation can fail for operational reasons unrelated to the input contract. |
| FAIL012 | Multiple failure modes collapse into one sentinel | risk | hazard | on | Later combined catalog. | Distinct exception or error paths return the same sentinel. | `{symbol}` collapses `{failure_count}` failure modes into `{sentinel}`, forcing callers to guess what happened. |
| FAIL013 | Cleanup can mask the original failure | risk | hazard | on | Later combined catalog. | Cleanup performed during an active exception can raise without preserving the original exception. | `{cleanup}` can raise while handling `{original_exception}`, replacing the failure that triggered cleanup. |
| FAIL014 | Retry has no bounded policy | risk | hazard | on | Later combined catalog. | A retry loop has no attempt, deadline, cancellation, or backoff bound. | `{symbol}` retries `{effect}` without an attempt limit, deadline, or cancellation boundary. |
| FAIL015 | Error handling mutates durable state | risk | hazard | on | Later combined catalog. | An exception handler writes durable state before failure is resolved or re-raised. | The `{exception}` handler writes `{state}` before recovery completes, making error handling part of the durable transition. |
