# CONC rules

The CONC domain addresses concurrency safety in async code: task and state ownership, proper lock usage, and race conditions.

These rules are planned. None of them is available in a release yet.

Background reading on the hazards these rules are meant to describe:
[Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html) and
[Developing with asyncio](https://docs.python.org/3/library/asyncio-dev.html)
in the Python standard library documentation.

| ID | Rule | Default | Concern |
|---|---|---|---|
| CONC001 | Shared state across await | on | hazard |
| CONC002 | Lock held across await | on | hazard |
| CONC003 | Blocking call in async | on | hazard |
| CONC004 | Concurrency primitive mismatch | on | hazard |
| CONC005 | Detached task has no owner | on | hazard |
| CONC006 | Inconsistent lock order | on | hazard |
| CONC007 | Race or deadlock observed | observe | hazard |
| CONC008 | Async shared scope mutation | on | hazard |
| CONC009 | Async state has no task owner | on | hazard |
| CONC010 | Async lifecycle is not awaited or closed | on | hazard |
| CONC011 | External await has no timeout boundary | on | review |
| CONC012 | Cancellation path can leave partial state | on | hazard |

## Rule details

### CONC001 Shared state across await

- **Claim:** risk
- **Detection/default:** Shared state is read, an `await` occurs, then state is written from the stale read
- **Message template:** `counter` is read before an `await` and written afterward, allowing another task to invalidate the update.

### CONC002 Lock held across await

- **Claim:** risk
- **Detection/default:** Async code awaits while holding a lock or semaphore
- **Message template:** `{symbol}` matches lock held across await: Async code awaits while holding a lock or semaphore.

### CONC003 Blocking call in async

- **Claim:** risk
- **Detection/default:** Async function reaches a known blocking primitive without delegation
- **Message template:** `{symbol}` matches blocking call in async: Async function reaches a known blocking primitive without delegation.

### CONC004 Concurrency primitive mismatch

- **Claim:** risk
- **Detection/default:** Coordination primitive is used outside the thread, task or process domain it protects
- **Message template:** `{symbol}` matches concurrency primitive mismatch: Coordination primitive is used outside the thread, task or process domain it protects.

### CONC005 Detached task has no owner

- **Claim:** risk
- **Detection/default:** Created task or submitted work has no retained, awaited or supervised handle
- **Message template:** `{symbol}` matches detached task: Created task or submitted work has no retained, awaited or supervised handle.

### CONC006 Inconsistent lock order

- **Claim:** risk
- **Detection/default:** Different paths acquire the same locks in different orders
- **Message template:** `{symbol}` matches inconsistent lock order: Different paths acquire the same locks in different orders.

### CONC007 Race or deadlock observed

- **Claim:** defect
- **Detection/default:** Instrumentation observes conflicting access, circular waiting or schedule-dependent failure
- **Message template:** `{symbol}` matches race or deadlock observed: Instrumentation observes conflicting access, circular waiting or schedule-dependent failure.

### CONC008 Async shared scope mutation

- **Claim:** risk
- **Detection/default:** Async function writes a `global` or `nonlocal` binding
- **Message template:** `{symbol}` matches async shared scope mutation: Async function writes a `global` or `nonlocal` binding.

### CONC009 Async state has no task owner

- **Claim:** risk
- **Detection/default:** own + cf + (cg or run)
- **Message template:** Three async functions mutate the same scope binding across suspension points without an identified task-local owner.

### CONC010 Async lifecycle is not awaited or closed

- **Claim:** risk
- **Detection/default:** An async iterator, context, stream, process, or client is created without an observed await/close/exit owner.
- **Message template:** `{resource}` is created in `{symbol}` without an observed await, close, or async-context owner.

### CONC011 External await has no timeout boundary

- **Claim:** design
- **Detection/default:** An external await is not dominated by a configured timeout or cancellation scope.
- **Message template:** `{symbol}` awaits `{effect}` without an observed timeout or cancellation boundary.

### CONC012 Cancellation path can leave partial state

- **Claim:** risk
- **Detection/default:** Owned state is mutated across a suspension point without rollback or cancellation-safe ordering.
- **Message template:** `{symbol}` mutates `{state}` across an `await`, so cancellation can expose a partially completed transition.
