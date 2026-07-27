# CONTRACT rules

CONTRACT rules are planned. None of them is implemented today, and nothing on
this page is available to run.

CONTRACT rules define explicit agreements between operations and callers about parameter types, return semantics, and behavioral patterns. These rules flag parameter design issues, type contract friction, and hidden complexity in function signatures that force callers to reason about implementation details.

The domain rests on design by contract, the idea Bertrand Meyer developed in
Eiffel: an operation states what it requires and what it guarantees, and the
signature is where that statement lives. Martin Fowler's
[Command Query Separation](https://martinfowler.com/bliki/CommandQuerySeparation.html)
summarizes Meyer's framing of the caller-facing side of that agreement.
[PEP 3102](https://peps.python.org/pep-3102/) covers keyword-only arguments,
the Python mechanism behind several of the signature rules below.

| ID          | Rule                                          | Default | Concern |
| ----------- | --------------------------------------------- | ------- | ------- |
| CONTRACT001 | Untyped dict parameter                        | on      | review  |
| CONTRACT002 | Untyped dict return                           | on      | review  |
| CONTRACT003 | Many operation arguments                      | on      | review  |
| CONTRACT004 | Optional not keyword only                     | on      | review  |
| CONTRACT005 | Mutually exclusive flags                      | on      | hazard  |
| CONTRACT006 | Unchecked any operation                       | on      | hazard  |
| CONTRACT007 | Positional record return                      | on      | review  |
| CONTRACT008 | Positional dataclass ambiguity                | on      | hazard  |
| CONTRACT009 | Type contract friction                        | on      | review  |
| CONTRACT010 | Function signature encodes multiple workflows | on      | review  |

## Rule detail

### CONTRACT001 Untyped dict parameter

**Claim.** design

**Detection/default.** `dict[str, Any]`/`dict[str, object]` as operation input

**Message template.** `{symbol}` matches untyped dict parameter: `dict[str, Any]`/`dict[str, object]` as operation input.

### CONTRACT002 Untyped dict return

**Claim.** design

**Detection/default.** Same in return position

**Message template.** `{symbol}` matches untyped dict return: Same in return position.

### CONTRACT003 Many operation arguments

**Claim.** design

**Detection/default.** Operation inputs only. 4 weak, 5 or 6 moderate, 7+ strong

**Message template.** `{symbol}` exposes `{actual}` operation inputs, increasing the contract a caller must understand at once.

### CONTRACT004 Optional not keyword only

**Claim.** design

**Detection/default.** Defaulted parameter reachable positionally

**Message template.** Defaulted parameter `{parameter}` remains positional, allowing call sites to hide which option they change.

### CONTRACT005 Mutually exclusive flags

**Claim.** risk

**Detection/default.** ≥2 booleans where only one may be true

**Message template.** `{symbol}` accepts `{flag_count}` flags with `{representable}` combinations although only `{valid}` are valid.

### CONTRACT006 Unchecked any operation

**Claim.** risk

**Detection/default.** An `Any`-typed value is called, indexed or attribute-accessed

**Message template.** `value` is typed as `Any` but requires `.save()`, so the implementation knows a contract that the annotation omits.

### CONTRACT007 Positional record return

**Claim.** design

**Detection/default.** Function returns a tuple with at least three semantically distinct values

**Message template.** `inspect()` returns four positional values whose meanings are unavailable without reading the implementation.

### CONTRACT008 Positional dataclass ambiguity

**Claim.** risk

**Detection/default.** Dataclass exposes more than three positional fields or adjacent same-typed fields

**Message template.** `Connection` exposes four positional `str` fields that the type checker cannot distinguish when transposed.

### CONTRACT009 Type contract friction

**Claim.** design

**Detection/default.** shp + (cg or cf)

**Message template.** value is typed as Any but is repeatedly cast, narrowed and ignored around the same missing contract.

### CONTRACT010 Function signature encodes multiple workflows

**Claim.** design

**Detection/default.** Disjoint parameter subsets are used on mutually exclusive paths.

**Message template.** `{symbol}` has `{workflow_count}` mutually exclusive parameter subsets, so one signature represents multiple workflows.
