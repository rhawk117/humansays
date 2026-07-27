# CONC rules

The CONC domain addresses concurrency safety in async code: task and state ownership, proper lock usage, and race conditions.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| CONC001 | Shared state across await | risk | hazard | on | HS-CONC-01 | Shared state is read, an `await` occurs, then state is written from the stale read | `counter` is read before an `await` and written afterward, allowing another task to invalidate the update. |
| CONC002 | Lock held across await | risk | hazard | on | HS-CONC-02 | Async code awaits while holding a lock or semaphore | `{symbol}` matches lock held across await: Async code awaits while holding a lock or semaphore. |
| CONC003 | Blocking call in async | risk | hazard | on | HS-CONC-03 | Async function reaches a known blocking primitive without delegation | `{symbol}` matches blocking call in async: Async function reaches a known blocking primitive without delegation. |
| CONC004 | Concurrency primitive mismatch | risk | hazard | on | HS-CONC-04 | Coordination primitive is used outside the thread, task or process domain it protects | `{symbol}` matches concurrency primitive mismatch: Coordination primitive is used outside the thread, task or process domain it protects. |
| CONC005 | Detached task has no owner | risk | hazard | on | HS-CONC-05 | Created task or submitted work has no retained, awaited or supervised handle | `{symbol}` matches detached task: Created task or submitted work has no retained, awaited or supervised handle. |
| CONC006 | Inconsistent lock order | risk | hazard | on | HS-CONC-06 | Different paths acquire the same locks in different orders | `{symbol}` matches inconsistent lock order: Different paths acquire the same locks in different orders. |
| CONC007 | Race or deadlock observed | defect | hazard | observe | HS-CONC-07 | Instrumentation observes conflicting access, circular waiting or schedule-dependent failure | `{symbol}` matches race or deadlock observed: Instrumentation observes conflicting access, circular waiting or schedule-dependent failure. |
| CONC008 | Async shared scope mutation | risk | hazard | on | HS-CONC-08 | Async function writes a `global` or `nonlocal` binding | `{symbol}` matches async shared scope mutation: Async function writes a `global` or `nonlocal` binding. |
| CONC009 | Async state has no task owner | risk | hazard | on | HS-FIND-17 | own + cf + (cg or run) | Three async functions mutate the same scope binding across suspension points without an identified task-local owner. |
| CONC010 | Async lifecycle is not awaited or closed | risk | hazard | on | Later combined catalog. | An async iterator, context, stream, process, or client is created without an observed await/close/exit owner. | `{resource}` is created in `{symbol}` without an observed await, close, or async-context owner. |
| CONC011 | External await has no timeout boundary | design | review | on | Later combined catalog. | An external await is not dominated by a configured timeout or cancellation scope. | `{symbol}` awaits `{effect}` without an observed timeout or cancellation boundary. |
| CONC012 | Cancellation path can leave partial state | risk | hazard | on | Later combined catalog. | Owned state is mutated across a suspension point without rollback or cancellation-safe ordering. | `{symbol}` mutates `{state}` across an `await`, so cancellation can expose a partially completed transition. |
