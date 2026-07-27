# CONTRACT rules

CONTRACT rules define explicit agreements between operations and callers about parameter types, return semantics, and behavioral patterns. These rules flag parameter design issues, type contract friction, and hidden complexity in function signatures that force callers to reason about implementation details.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| CONTRACT001 | Untyped dict parameter | design | review | on | HS-PURPOSE-05 | `dict[str, Any]`/`dict[str, object]` as operation input | `{symbol}` matches untyped dict parameter: `dict[str, Any]`/`dict[str, object]` as operation input. |
| CONTRACT002 | Untyped dict return | design | review | on | HS-PURPOSE-06 | Same in return position | `{symbol}` matches untyped dict return: Same in return position. |
| CONTRACT003 | Many operation arguments | design | review | on | HS-ARGS-01 | Operation inputs only. 4 weak, 5–6 moderate, 7+ strong | `{symbol}` exposes `{actual}` operation inputs, increasing the contract a caller must understand at once. |
| CONTRACT004 | Optional not keyword only | design | review | on | HS-ARGS-06 | Defaulted parameter reachable positionally | Defaulted parameter `{parameter}` remains positional, allowing call sites to hide which option they change. |
| CONTRACT005 | Mutually exclusive flags | risk | hazard | on | HS-ARGS-09 | ≥2 booleans where only one may be true | `{symbol}` accepts `{flag_count}` flags with `{representable}` combinations although only `{valid}` are valid. |
| CONTRACT006 | Unchecked any operation | risk | hazard | on | HS-PURPOSE-13 | An `Any`-typed value is called, indexed or attribute-accessed | `value` is typed as `Any` but requires `.save()`, so the implementation knows a contract that the annotation omits. |
| CONTRACT007 | Positional record return | design | review | on | HS-PURPOSE-14 | Function returns a tuple with at least three semantically distinct values | `inspect()` returns four positional values whose meanings are unavailable without reading the implementation. |
| CONTRACT008 | Positional dataclass ambiguity | risk | hazard | on | HS-INIT-11 | Dataclass exposes more than three positional fields or adjacent same-typed fields | `Connection` exposes four positional `str` fields that the type checker cannot distinguish when transposed. |
| CONTRACT009 | Type contract friction | design | review | on | HS-FIND-18 | shp + (cg or cf) | value is typed as Any but is repeatedly cast, narrowed and ignored around the same missing contract. |
| CONTRACT010 | Function signature encodes multiple workflows | design | review | on | Later combined catalog. | Disjoint parameter subsets are used on mutually exclusive paths. | `{symbol}` has `{workflow_count}` mutually exclusive parameter subsets, so one signature represents multiple workflows. |
