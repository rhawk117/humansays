# COUP rules

COUP rules detect coupling problems in Python code, including undeclared
dependencies, hidden inputs from the environment and time, and excessive object
coupling.

Dependency visibility, dependency surface, and change coupling.

None of the rules below are implemented yet. They are planned.

Background reading: Martin Fowler's
[Reducing Coupling](https://martinfowler.com/ieeeSoftware/coupling.pdf) and the
[cohesion](<https://en.wikipedia.org/wiki/Cohesion_(computer_science)>) overview.

| ID      | Rule                           | Default | Concern |
| ------- | ------------------------------ | ------- | ------- |
| COUP001 | Undeclared dependency          | on      | hazard  |
| COUP002 | Env read in logic              | on      | hazard  |
| COUP003 | Clock read inline              | on      | hazard  |
| COUP004 | Randomness inline              | on      | hazard  |
| COUP005 | Settings singleton access      | on      | review  |
| COUP006 | Hidden dependency surface      | on      | hazard  |
| COUP007 | Untestable without environment | on      | hazard  |
| COUP008 | Single attribute dependency    | on      | review  |

## Rule details

### COUP001 Undeclared dependency

**Claim.** risk

**Detection/default.** Body reaches a name absent from signature and instance state

**Message template.** `{symbol}` depends on `{dependency}` without receiving it through its signature or owned instance state.

### COUP002 Env read in logic

**Claim.** risk

**Detection/default.** `os.environ`/`getenv` below module level

**Message template.** `{symbol}` reads `{variable}` from the environment inside application logic, hiding a replaceable input.

### COUP003 Clock read inline

**Claim.** risk

**Detection/default.** `datetime.now`, `time.time` in a decision path

**Message template.** `{symbol}` reads the clock inside a decision path, so identical explicit inputs can produce different decisions.

### COUP004 Randomness inline

**Claim.** risk

**Detection/default.** `random.*`, `uuid4`, `secrets.*` in a decision path

**Message template.** `{symbol}` reads randomness inside a decision path without an injection point.

### COUP005 Settings singleton access

**Claim.** design

**Detection/default.** Import-time-constructed config accessed deep in logic

**Message template.** `{symbol}` reaches the process-wide settings singleton `{name}` instead of declaring configuration as a dependency.

### COUP006 Hidden dependency surface

**Claim.** risk

**Detection/default.** eff + own

**Message template.** `{symbol}` depends on `{dependencies}` through ambient state and effect access rather than its declared contract.

### COUP007 Untestable without environment

**Claim.** risk

**Detection/default.** eff + own + cg

**Message template.** `{unit}` cannot be constructed or exercised without `{environment}`, according to independent test, ownership, and effect evidence.

### COUP008 Single attribute dependency

**Claim.** design

**Detection/default.** Function accepts an object but only reads one attribute from it

**Message template.** `send_notice()` accepts `User` but depends only on `user.email`, unnecessarily coupling the function to the entire class.
