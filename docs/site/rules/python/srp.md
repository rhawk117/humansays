# SRP rules

Single Responsibility rules detect violations of cohesion and responsibility concentration—situations where a class or function accumulates multiple independent reasons to change.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| SRP001 | Role conflict | design | review | on | HS-PURPOSE-10 | Decides, performs I/O, and formats output in one body | `{symbol}` decides policy, performs `{effects}`, and formats output in one body. |
| SRP002 | Effect in domain type | design | review | on | HS-EFFECT-10 | I/O inside a value object, DTO or entity | `{type}` performs `{effect}` even though it is used as a domain value or data carrier. |
| SRP003 | Mixed responsibilities | design | review | on | HS-FIND-01 | own + eff + (shp or cf) | `{symbol}` combines `{responsibilities}` across independent ownership, effect, and control-flow evidence. |
| SRP004 | Mixed abstraction levels | design | review | on | HS-SHAPE-09 | Raw I/O construction alongside domain decisions | `{symbol}` combines domain decisions with low-level `{effect}` construction in the same abstraction layer. |
| SRP005 | Low field cohesion | design | review | on | HS-CLASS-01 | Method/field graph splits into ≥2 components | `{class}` splits into `{component_count}` disconnected method/field components. |
| SRP006 | God constructor | design | review | on | HS-CLASS-10 | Constructor assigns > 8 fields | `{class}.__init__` establishes `{actual}` fields, indicating construction and responsibility pressure. |
| SRP007 | Unclassifiable unit | design | review | on | HS-FIND-03 | nam + shp + eff | `{symbol}` has no dominant role across its name, data flow, effects, and return behavior. |
| SRP008 | Incohesive class | design | review | on | HS-FIND-05 | own + shp | `{class}` contains `{component_count}` independent method/field components with little shared state. |
| SRP009 | Logging mixed with domain mutation | design | review | on | Later combined catalog. | A function mutates domain state and also owns log/report formatting policy. | `{symbol}` mutates `{state}` and builds `{reporting}` output in the same responsibility boundary. |
| SRP010 | Configuration object drives unrelated workflows | design | review | on | Later combined catalog. | A configuration object is read by disjoint method/effect clusters that select separate workflows. | `{type}` supplies `{workflow_count}` unrelated workflow clusters, so configuration has become a responsibility switchboard. |
| SRP011 | Data object used as behavior switchboard | design | review | on | Later combined catalog. | Many branches dispatch behavior from one data object's tag/type fields. | `{symbol}` selects `{branch_count}` behaviors from `{object}.{field}`, making a data carrier own workflow selection indirectly. |
