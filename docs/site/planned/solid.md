# SOLID rules

SOLID rules cover how responsibility and dependency are distributed across
types: a unit that accumulates several independent reasons to change, a
conditional that grows a branch every time the domain gains a variant, an
override that narrows what its base promised, or a dependency the signature
never declares.

The group is flat. Every rule carries a `SOLID###` identifier, and `SOLID` is
the only selector token, configuration key, and heading for the group.

None of the rules below are implemented yet. They are planned.

Background reading:
[Robert C. Martin on the Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html),
[Extract Class](https://refactoring.com/catalog/extractClass.html) in Martin
Fowler's refactoring catalog, and Fowler's
[Reducing Coupling](https://martinfowler.com/ieeeSoftware/coupling.pdf).

| ID       | Rule                                            | Default | Concern |
| -------- | ----------------------------------------------- | ------- | ------- |
| SOLID001 | Role conflict                                   | on      | review  |
| SOLID002 | Effect in domain type                           | on      | review  |
| SOLID003 | Mixed responsibilities                          | on      | review  |
| SOLID004 | Mixed abstraction levels                        | on      | review  |
| SOLID005 | Low field cohesion                              | on      | review  |
| SOLID006 | God constructor                                 | on      | review  |
| SOLID007 | Unclassifiable unit                             | on      | review  |
| SOLID008 | Incohesive class                                | on      | review  |
| SOLID009 | Logging mixed with domain mutation              | on      | review  |
| SOLID010 | Configuration object drives unrelated workflows | on      | review  |
| SOLID011 | Data object used as behavior switchboard        | on      | review  |
| SOLID012 | Boolean mode switch                             | on      | review  |
| SOLID013 | Repeated type or value dispatch                 | on      | review  |
| SOLID014 | Function signature encodes multiple workflows   | on      | review  |
| SOLID015 | Concrete factory return                         | on      | hazard  |
| SOLID016 | Name mangled shadow                             | on      | hazard  |
| SOLID017 | Undeclared dependency                           | on      | hazard  |
| SOLID018 | Env read in logic                               | on      | hazard  |
| SOLID019 | Clock read inline                               | on      | hazard  |
| SOLID020 | Randomness inline                               | on      | hazard  |
| SOLID021 | Settings singleton access                       | on      | review  |
| SOLID022 | Hidden dependency surface                       | on      | hazard  |
| SOLID023 | Untestable without environment                  | on      | hazard  |

## Rule details

### SOLID001 Role conflict

**Claim.** design

**Detection/default.** Decides, performs I/O, and formats output in one body

**Message template.** `{symbol}` decides policy, performs `{effects}`, and formats output in one body.

### SOLID002 Effect in domain type

**Claim.** design

**Detection/default.** I/O inside a value object, DTO or entity

**Message template.** `{type}` performs `{effect}` even though it is used as a domain value or data carrier.

### SOLID003 Mixed responsibilities

**Claim.** design

**Detection/default.** own + eff + (shp or cf)

**Message template.** `{symbol}` combines `{responsibilities}` across independent ownership, effect, and control-flow evidence.

### SOLID004 Mixed abstraction levels

**Claim.** design

**Detection/default.** Raw I/O construction alongside domain decisions

**Message template.** `{symbol}` combines domain decisions with low-level `{effect}` construction in the same abstraction layer.

### SOLID005 Low field cohesion

**Claim.** design

**Detection/default.** Method/field graph splits into ≥2 components

**Message template.** `{class}` splits into `{component_count}` disconnected method/field components.

### SOLID006 God constructor

**Claim.** design

**Detection/default.** Constructor assigns > 8 fields

**Message template.** `{class}.__init__` establishes `{actual}` fields, indicating construction and responsibility pressure.

### SOLID007 Unclassifiable unit

**Claim.** design

**Detection/default.** nam + shp + eff

**Message template.** `{symbol}` has no dominant role across its name, data flow, effects, and return behavior.

### SOLID008 Incohesive class

**Claim.** design

**Detection/default.** own + shp

**Message template.** `{class}` contains `{component_count}` independent method/field components with little shared state.

### SOLID009 Logging mixed with domain mutation

**Claim.** design

**Detection/default.** A function mutates domain state and also owns log/report formatting policy.

**Message template.** `{symbol}` mutates `{state}` and builds `{reporting}` output in the same responsibility boundary.

### SOLID010 Configuration object drives unrelated workflows

**Claim.** design

**Detection/default.** A configuration object is read by disjoint method/effect clusters that select separate workflows.

**Message template.** `{type}` supplies `{workflow_count}` unrelated workflow clusters, so configuration has become a responsibility switchboard.

### SOLID011 Data object used as behavior switchboard

**Claim.** design

**Detection/default.** Many branches dispatch behavior from one data object's tag/type fields.

**Message template.** `{symbol}` selects `{branch_count}` behaviors from `{object}.{field}`, making a data carrier own workflow selection indirectly.

### SOLID012 Boolean mode switch

**Claim.** design

**Detection/default.** Boolean selecting between two behaviors in the body

**Message template.** Boolean `{parameter}` selects between `{mode_count}` workflows inside `{symbol}`.

### SOLID013 Repeated type or value dispatch

**Claim.** design

**Detection/default.** Conditional chain selects behavior from one type, tag, enum or literal discriminator

**Message template.** Eight branches differ only by the selected callable, so this conditional is functioning as a dispatch dictionary.

### SOLID014 Function signature encodes multiple workflows

**Claim.** design

**Detection/default.** Disjoint parameter subsets are used on mutually exclusive paths.

**Message template.** `{symbol}` has `{workflow_count}` mutually exclusive parameter subsets, so one signature represents multiple workflows.

### SOLID015 Concrete factory return

**Claim.** risk

**Detection/default.** Non-final classmethod constructs `cls(...)` but returns the containing class type

**Message template.** `Request.from_bytes()` constructs `cls` but returns `Request`, discarding the subclass-preserving contract of `Self`.

### SOLID016 Name mangled shadow

**Claim.** risk

**Detection/default.** Base and subclass declare the same source-level mangled name

**Message template.** `Child.__load` does not override `Base.__load` because the two methods are mangled into different names.

### SOLID017 Undeclared dependency

**Claim.** risk

**Detection/default.** Body reaches a name absent from signature and instance state

**Message template.** `{symbol}` depends on `{dependency}` without receiving it through its signature or owned instance state.

### SOLID018 Env read in logic

**Claim.** risk

**Detection/default.** `os.environ`/`getenv` below module level

**Message template.** `{symbol}` reads `{variable}` from the environment inside application logic, hiding a replaceable input.

### SOLID019 Clock read inline

**Claim.** risk

**Detection/default.** `datetime.now`, `time.time` in a decision path

**Message template.** `{symbol}` reads the clock inside a decision path, so identical explicit inputs can produce different decisions.

### SOLID020 Randomness inline

**Claim.** risk

**Detection/default.** `random.*`, `uuid4`, `secrets.*` in a decision path

**Message template.** `{symbol}` reads randomness inside a decision path without an injection point.

### SOLID021 Settings singleton access

**Claim.** design

**Detection/default.** Import-time-constructed config accessed deep in logic

**Message template.** `{symbol}` reaches the process-wide settings singleton `{name}` instead of declaring configuration as a dependency.

### SOLID022 Hidden dependency surface

**Claim.** risk

**Detection/default.** eff + own

**Message template.** `{symbol}` depends on `{dependencies}` through ambient state and effect access rather than its declared contract.

### SOLID023 Untestable without environment

**Claim.** risk

**Detection/default.** eff + own + cg

**Message template.** `{unit}` cannot be constructed or exercised without `{environment}`, according to independent test, ownership, and effect evidence.
