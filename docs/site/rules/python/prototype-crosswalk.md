# Prototype crosswalk

This page maps the prototype PY001–PY022 checks to their disposition in the new ruleset. Each row shows a prototype check and its corresponding rule or status in the final catalog.

## 8. Prototype `PY001`–`PY022` crosswalk

| Prototype ID | Prototype check | Final disposition |
|---|---|---|
| `PY001` | many arguments | HS-ARGS-01 |
| `PY002` | boolean modes | HS-ARGS-03 |
| `PY003` | deep nesting | HS-SHAPE-03 |
| `PY004` | shared mutable state | HS-STATE-06 |
| `PY005` | broad exception | HS-FAIL-01/02/03 |
| `PY006` | mutation owners | HS-STATE-04 |
| `PY007` | mixed boundaries | HS-EFFECT-06 and HS-FIND-01/02 |
| `PY008` | low class cohesion | HS-CLASS-01 and HS-FIND-05 |
| `PY009` | long function | HS-SHAPE-01 |
| `PY010` | comments | omitted: raw comment count was noisy and duplicated narration evidence |
| `PY011` | docstrings | omitted: raw docstring count did not establish a structural problem |
| `PY012` | many class attributes | HS-CLASS-03 |
| `PY013` | attribute prefix clusters | HS-CLASS-05 |
| `PY014` | validated argument bundle | HS-INIT-07 |
| `PY015` | static method | NIT rule; reviewer hint only |
| `PY016` | lambda | NIT rule; reviewer hint only |
| `PY017` | long file | HS-SHAPE-10 |
| `PY018` | many base classes | HS-CLASS-08 |
| `PY019` | many branches | HS-SHAPE-04 |
| `PY020` | future annotations | omitted: version-dependent modernization belongs to Ruff and loses value on newer Python |
| `PY021` | lazy import | IDIOM rule; reviewer hint only |
| `PY022` | dense function | HS-SHAPE-02 |
