# COUP rules

COUP rules detect coupling problems in Python code, including undeclared dependencies, hidden inputs from the environment and time, and excessive object coupling.

Dependency visibility, dependency surface, and change coupling.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| COUP001 | Undeclared dependency | risk | hazard | on | HS-PURPOSE-11 | Body reaches a name absent from signature and instance state | `{symbol}` depends on `{dependency}` without receiving it through its signature or owned instance state. |
| COUP002 | Env read in logic | risk | hazard | on | HS-INPUT-01 | `os.environ`/`getenv` below module level | `{symbol}` reads `{variable}` from the environment inside application logic, hiding a replaceable input. |
| COUP003 | Clock read inline | risk | hazard | on | HS-INPUT-02 | `datetime.now`, `time.time` in a decision path | `{symbol}` reads the clock inside a decision path, so identical explicit inputs can produce different decisions. |
| COUP004 | Randomness inline | risk | hazard | on | HS-INPUT-03 | `random.*`, `uuid4`, `secrets.*` in a decision path | `{symbol}` reads randomness inside a decision path without an injection point. |
| COUP005 | Settings singleton access | design | review | on | HS-INPUT-06 | Import-time-constructed config accessed deep in logic | `{symbol}` reaches the process-wide settings singleton `{name}` instead of declaring configuration as a dependency. |
| COUP006 | Hidden dependency surface | risk | hazard | on | HS-FIND-08 | eff + own | `{symbol}` depends on `{dependencies}` through ambient state and effect access rather than its declared contract. |
| COUP007 | Untestable without environment | risk | hazard | on | HS-FIND-09 | eff + own + cg | `{unit}` cannot be constructed or exercised without `{environment}`, according to independent test, ownership, and effect evidence. |
| COUP008 | Single attribute dependency | design | review | on | HS-ARGS-10 | Function accepts an object but only reads one attribute from it | `send_notice()` accepts `User` but depends only on `user.email`, unnecessarily coupling the function to the entire class. |
