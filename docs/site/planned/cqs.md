# CQS rules

These rules flag violations of command-query separation, where operations that
sound like observation also perform mutation or external effects. The promise
each rule tests is one made by an identifier — a name that reads as a question
attached to a body that answers with a side effect.

None of the rules below are implemented yet. They are planned.

Background reading: Bertrand Meyer's rule as described by
[Martin Fowler](https://martinfowler.com/bliki/CommandQuerySeparation.html),
and the
[command-query separation](https://en.wikipedia.org/wiki/Command%E2%80%93query_separation)
overview.

| ID     | Rule                                    | Default | Concern |
| ------ | --------------------------------------- | ------- | ------- |
| CQS001 | Query mutates owned state               | on      | hazard  |
| CQS002 | Query performs I/O                      | on      | review  |
| CQS003 | Mutation disguised as calculation       | on      | hazard  |
| CQS004 | Caller object mutation                  | on      | hazard  |
| CQS005 | Destructive mutation hidden from caller | on      | hazard  |
| CQS006 | Persistence hidden in helper            | on      | hazard  |
| CQS007 | Helper name hides external effects      | on      | review  |

## Rule details

### CQS001 Query mutates owned state

**Claim.** risk

**Detection/default.** `get_*`/`is_*`/`has_*`/`find_*` with non-empty field writes

**Message template.** `{symbol}` reads like a query but writes `{fields}`, so callers cannot treat it as observation-only.

### CQS002 Query performs I/O

**Claim.** design

**Detection/default.** Query-named function reaching an effect boundary

**Message template.** `{symbol}` reads like a query but reaches `{effects}`, making ordinary-looking observation perform external work.

### CQS003 Mutation disguised as calculation

**Claim.** risk

**Detection/default.** Pure-sounding name writing to caller-owned objects

**Message template.** `{symbol}` sounds like a calculation but mutates caller-owned `{target}`.

### CQS004 Caller object mutation

**Claim.** risk

**Detection/default.** Mutates a parameter the caller owns

**Message template.** `{symbol}` mutates caller-owned `{parameter}`. Should the mutation be visible from the signature?

### CQS005 Destructive mutation hidden from caller

**Claim.** risk

**Detection/default.** own + (nam or shp)

**Message template.** `normalize()` deletes and rewrites entries in its input mapping. Should a caller be able to see that from the name?

### CQS006 Persistence hidden in helper

**Claim.** risk

**Detection/default.** A generic helper name reaches a database write or commit boundary.

**Message template.** Helper `{helper}` performs `{persistence_effect}`. Should the name communicate durable mutation?

### CQS007 Helper name hides external effects

**Claim.** design

**Detection/default.** A generic or pure-looking helper reaches network, filesystem, database, notification, or subprocess effects.

**Message template.** Helper `{helper}` performs `{effects}`. Should a caller be able to infer that from the name?
