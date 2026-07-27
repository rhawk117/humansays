# ERR rules

!!! warning "Not implemented"

    These rules are designed, not shipped. Nothing on this page runs in
    version `0.1.0a1`, which implements [19 rules](../rules/index.md).

ERR rules examine failure boundaries, recovery strategies, retries, and rollback logic. They identify risks in partial state updates, swallowed exceptions, and unordered external effects.

The discipline these rules describe is that a failure should stay
distinguishable from a normal result and should not be quietly replaced by a
later one. Python's
[errors and exceptions tutorial](https://docs.python.org/3/tutorial/errors.html)
covers the language semantics, and
[PEP 3134](https://peps.python.org/pep-3134/) specifies the exception chaining
that keeps an original failure visible when a second one is raised while
handling it.

| ID     | Rule                                              | Default | Concern |
| ------ | ------------------------------------------------- | ------- | ------- |
| ERR001 | Mutation between external effects                 | on      | hazard  |
| ERR002 | Unordered multi effect                            | on      | hazard  |
| ERR003 | Exception leaves partial state                    | on      | hazard  |
| ERR004 | Broad exception swallowed                         | on      | hazard  |
| ERR005 | Absence collapsed into failure                    | on      | hazard  |
| ERR006 | Retry without idempotence                         | on      | hazard  |
| ERR007 | Error message only                                | on      | review  |
| ERR008 | Side effect orchestration risk                    | on      | hazard  |
| ERR009 | Ambiguous failure contract                        | on      | hazard  |
| ERR010 | Silent infrastructure failure                     | on      | hazard  |
| ERR011 | External call inside validation logic             | on      | review  |
| ERR012 | Multiple failure modes collapse into one sentinel | on      | hazard  |
| ERR013 | Cleanup can mask the original failure             | on      | hazard  |
| ERR014 | Retry has no bounded policy                       | on      | hazard  |
| ERR015 | Error handling mutates durable state              | on      | hazard  |

## Rule detail

### ERR001 Mutation between external effects { #ERR001 }

Claim
:   risk

Detection
:   Mutation, then effect, then mutation

Message
:   `{symbol}` mutates state before and after `{effect}`, exposing a partial-state window if the effect fails.

### ERR002 Unordered multi effect { #ERR002 }

Claim
:   risk

Detection
:   ≥2 effects with no transaction or compensation

Message
:   `{symbol}` performs `{effect_count}` external effects without an observed transaction, compensation, or idempotent boundary.

### ERR003 Exception leaves partial state { #ERR003 }

Claim
:   risk

Detection
:   Raise between two writes to the same owner

Message
:   `{symbol}` can raise after `{completed_writes}` of `{total_writes}` writes, leaving `{owner}` partially updated.

### ERR004 Broad exception swallowed { #ERR004 }

Claim
:   risk

Detection
:   `except Exception` with `pass`/`return None` body

Message
:   `{symbol}` catches `{exception}` and continues with `{fallback}`, discarding the original failure.

### ERR005 Absence collapsed into failure { #ERR005 }

Claim
:   risk

Detection
:   Infrastructure error converted to `None` return

Message
:   `{symbol}` converts `{exception}` into `None`, collapsing infrastructure failure into ordinary absence.

### ERR006 Retry without idempotence { #ERR006 }

Claim
:   risk

Detection
:   Retry loop wrapping a mutating effect

Message
:   `{symbol}` retries mutating effect `{effect}` without an observed idempotency key, rollback, or compensation policy.

### ERR007 Error message only { #ERR007 }

Claim
:   design

Detection
:   Failure distinguished by message string, not type

Message
:   `{symbol}` distinguishes failure behavior by matching message text instead of an explicit exception or result contract.

### ERR008 Side effect orchestration risk { #ERR008 }

Claim
:   risk

Detection
:   eff + cf

Message
:   `{symbol}` coordinates `{effects}` across `{failure_regions}` failure regions without one visible recovery boundary.

### ERR009 Ambiguous failure contract { #ERR009 }

Claim
:   risk

Detection
:   cf + eff

Message
:   `{symbol}` exposes `{failure_modes}` failure modes through the same ambiguous return or exception contract.

### ERR010 Silent infrastructure failure { #ERR010 }

Claim
:   risk

Detection
:   cf + eff

Message
:   `{symbol}` suppresses `{exception}` from `{effect}`, making infrastructure failure indistinguishable from success.

### ERR011 External call inside validation logic { #ERR011 }

Claim
:   design

Detection
:   Validation reaches an external effect boundary.

Message
:   `{validator}` performs `{effect}` while deciding validity, so validation can fail for operational reasons unrelated to the input contract.

### ERR012 Multiple failure modes collapse into one sentinel { #ERR012 }

Claim
:   risk

Detection
:   Distinct exception or error paths return the same sentinel.

Message
:   `{symbol}` collapses `{failure_count}` failure modes into `{sentinel}`, forcing callers to guess what happened.

### ERR013 Cleanup can mask the original failure { #ERR013 }

Claim
:   risk

Detection
:   Cleanup performed during an active exception can raise without preserving the original exception.

Message
:   `{cleanup}` can raise while handling `{original_exception}`, replacing the failure that triggered cleanup.

### ERR014 Retry has no bounded policy { #ERR014 }

Claim
:   risk

Detection
:   A retry loop has no attempt, deadline, cancellation, or backoff bound.

Message
:   `{symbol}` retries `{effect}` without an attempt limit, deadline, or cancellation boundary.

### ERR015 Error handling mutates durable state { #ERR015 }

Claim
:   risk

Detection
:   An exception handler writes durable state before failure is resolved or re-raised.

Message
:   The `{exception}` handler writes `{state}` before recovery completes, making error handling part of the durable transition.
