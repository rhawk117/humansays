# SRP rules

Single Responsibility rules detect violations of cohesion and responsibility
concentration: situations where a class or function accumulates multiple
independent reasons to change.

None of the rules below are implemented yet. They are planned.

Background reading:
[Robert C. Martin on the Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html)
and [Extract Class](https://refactoring.com/catalog/extractClass.html) in
Martin Fowler's refactoring catalog.

| ID     | Rule                                            | Default | Concern |
| ------ | ----------------------------------------------- | ------- | ------- |
| SRP001 | Role conflict                                   | on      | review  |
| SRP002 | Effect in domain type                           | on      | review  |
| SRP003 | Mixed responsibilities                          | on      | review  |
| SRP004 | Mixed abstraction levels                        | on      | review  |
| SRP005 | Low field cohesion                              | on      | review  |
| SRP006 | God constructor                                 | on      | review  |
| SRP007 | Unclassifiable unit                             | on      | review  |
| SRP008 | Incohesive class                                | on      | review  |
| SRP009 | Logging mixed with domain mutation              | on      | review  |
| SRP010 | Configuration object drives unrelated workflows | on      | review  |
| SRP011 | Data object used as behavior switchboard        | on      | review  |

## Rule details

### SRP001 Role conflict

**Claim.** design

**Detection/default.** Decides, performs I/O, and formats output in one body

**Message template.** `{symbol}` decides policy, performs `{effects}`, and formats output in one body.

### SRP002 Effect in domain type

**Claim.** design

**Detection/default.** I/O inside a value object, DTO or entity

**Message template.** `{type}` performs `{effect}` even though it is used as a domain value or data carrier.

### SRP003 Mixed responsibilities

**Claim.** design

**Detection/default.** own + eff + (shp or cf)

**Message template.** `{symbol}` combines `{responsibilities}` across independent ownership, effect, and control-flow evidence.

### SRP004 Mixed abstraction levels

**Claim.** design

**Detection/default.** Raw I/O construction alongside domain decisions

**Message template.** `{symbol}` combines domain decisions with low-level `{effect}` construction in the same abstraction layer.

### SRP005 Low field cohesion

**Claim.** design

**Detection/default.** Method/field graph splits into ≥2 components

**Message template.** `{class}` splits into `{component_count}` disconnected method/field components.

### SRP006 God constructor

**Claim.** design

**Detection/default.** Constructor assigns > 8 fields

**Message template.** `{class}.__init__` establishes `{actual}` fields, indicating construction and responsibility pressure.

### SRP007 Unclassifiable unit

**Claim.** design

**Detection/default.** nam + shp + eff

**Message template.** `{symbol}` has no dominant role across its name, data flow, effects, and return behavior.

### SRP008 Incohesive class

**Claim.** design

**Detection/default.** own + shp

**Message template.** `{class}` contains `{component_count}` independent method/field components with little shared state.

### SRP009 Logging mixed with domain mutation

**Claim.** design

**Detection/default.** A function mutates domain state and also owns log/report formatting policy.

**Message template.** `{symbol}` mutates `{state}` and builds `{reporting}` output in the same responsibility boundary.

### SRP010 Configuration object drives unrelated workflows

**Claim.** design

**Detection/default.** A configuration object is read by disjoint method/effect clusters that select separate workflows.

**Message template.** `{type}` supplies `{workflow_count}` unrelated workflow clusters, so configuration has become a responsibility switchboard.

### SRP011 Data object used as behavior switchboard

**Claim.** design

**Detection/default.** Many branches dispatch behavior from one data object's tag/type fields.

**Message template.** `{symbol}` selects `{branch_count}` behaviors from `{object}.{field}`, making a data carrier own workflow selection indirectly.
