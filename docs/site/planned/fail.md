# FAIL rules

FAIL rules are planned. None of them is implemented today, and nothing on this
page is available to run.

FAIL rules examine failure boundaries, recovery strategies, retries, and rollback logic. They identify risks in partial state updates, swallowed exceptions, and unordered external effects.

The discipline these rules describe is that a failure should stay
distinguishable from a normal result and should not be quietly replaced by a
later one. Python's
[errors and exceptions tutorial](https://docs.python.org/3/tutorial/errors.html)
covers the language semantics, and
[PEP 3134](https://peps.python.org/pep-3134/) specifies the exception chaining
that keeps an original failure visible when a second one is raised while
handling it.

| ID | Rule | Default | Concern |
|---|---|---|---|
| FAIL001 | Mutation between external effects | on | hazard |
| FAIL002 | Unordered multi effect | on | hazard |
| FAIL003 | Exception leaves partial state | on | hazard |
| FAIL004 | Broad exception swallowed | on | hazard |
| FAIL005 | Absence collapsed into failure | on | hazard |
| FAIL006 | Retry without idempotence | on | hazard |
| FAIL007 | Error message only | on | review |
| FAIL008 | Side effect orchestration risk | on | hazard |
| FAIL009 | Ambiguous failure contract | on | hazard |
| FAIL010 | Silent infrastructure failure | on | hazard |
| FAIL011 | External call inside validation logic | on | review |
| FAIL012 | Multiple failure modes collapse into one sentinel | on | hazard |
| FAIL013 | Cleanup can mask the original failure | on | hazard |
| FAIL014 | Retry has no bounded policy | on | hazard |
| FAIL015 | Error handling mutates durable state | on | hazard |

## Rule detail

### FAIL001 Mutation between external effects

**Claim.** risk

**Detection/default.** Mutation, then effect, then mutation

**Message template.** `{symbol}` mutates state before and after `{effect}`, exposing a partial-state window if the effect fails.

### FAIL002 Unordered multi effect

**Claim.** risk

**Detection/default.** ≥2 effects with no transaction or compensation

**Message template.** `{symbol}` performs `{effect_count}` external effects without an observed transaction, compensation, or idempotent boundary.

### FAIL003 Exception leaves partial state

**Claim.** risk

**Detection/default.** Raise between two writes to the same owner

**Message template.** `{symbol}` can raise after `{completed_writes}` of `{total_writes}` writes, leaving `{owner}` partially updated.

### FAIL004 Broad exception swallowed

**Claim.** risk

**Detection/default.** `except Exception` with `pass`/`return None` body

**Message template.** `{symbol}` catches `{exception}` and continues with `{fallback}`, discarding the original failure.

### FAIL005 Absence collapsed into failure

**Claim.** risk

**Detection/default.** Infrastructure error converted to `None` return

**Message template.** `{symbol}` converts `{exception}` into `None`, collapsing infrastructure failure into ordinary absence.

### FAIL006 Retry without idempotence

**Claim.** risk

**Detection/default.** Retry loop wrapping a mutating effect

**Message template.** `{symbol}` retries mutating effect `{effect}` without an observed idempotency key, rollback, or compensation policy.

### FAIL007 Error message only

**Claim.** design

**Detection/default.** Failure distinguished by message string, not type

**Message template.** `{symbol}` distinguishes failure behavior by matching message text instead of an explicit exception or result contract.

### FAIL008 Side effect orchestration risk

**Claim.** risk

**Detection/default.** eff + cf

**Message template.** `{symbol}` coordinates `{effects}` across `{failure_regions}` failure regions without one visible recovery boundary.

### FAIL009 Ambiguous failure contract

**Claim.** risk

**Detection/default.** cf + eff

**Message template.** `{symbol}` exposes `{failure_modes}` failure modes through the same ambiguous return or exception contract.

### FAIL010 Silent infrastructure failure

**Claim.** risk

**Detection/default.** cf + eff

**Message template.** `{symbol}` suppresses `{exception}` from `{effect}`, making infrastructure failure indistinguishable from success.

### FAIL011 External call inside validation logic

**Claim.** design

**Detection/default.** Validation reaches an external effect boundary.

**Message template.** `{validator}` performs `{effect}` while deciding validity, so validation can fail for operational reasons unrelated to the input contract.

### FAIL012 Multiple failure modes collapse into one sentinel

**Claim.** risk

**Detection/default.** Distinct exception or error paths return the same sentinel.

**Message template.** `{symbol}` collapses `{failure_count}` failure modes into `{sentinel}`, forcing callers to guess what happened.

### FAIL013 Cleanup can mask the original failure

**Claim.** risk

**Detection/default.** Cleanup performed during an active exception can raise without preserving the original exception.

**Message template.** `{cleanup}` can raise while handling `{original_exception}`, replacing the failure that triggered cleanup.

### FAIL014 Retry has no bounded policy

**Claim.** risk

**Detection/default.** A retry loop has no attempt, deadline, cancellation, or backoff bound.

**Message template.** `{symbol}` retries `{effect}` without an attempt limit, deadline, or cancellation boundary.

### FAIL015 Error handling mutates durable state

**Claim.** risk

**Detection/default.** An exception handler writes durable state before failure is resolved or re-raised.

**Message template.** The `{exception}` handler writes `{state}` before recovery completes, making error handling part of the durable transition.
