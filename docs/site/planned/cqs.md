# CQS rules

These rules flag violations of command-query separation, where operations that
sound like observation also perform mutation or external effects. The promise
each rule tests is one made by an identifier — a name that reads as a question
attached to a body that answers with a side effect.

!!! warning "Not implemented"

    These rules are designed, not shipped. Nothing on this page runs in
    version `0.1.0a1`, which implements [19 rules](../rules/index.md).

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

### CQS001 Query mutates owned state { #CQS001 }

Claim
:   risk

Detection
:   `get_*`/`is_*`/`has_*`/`find_*` with non-empty field writes

Message
:   `{symbol}` reads like a query but writes `{fields}`, so callers cannot treat it as observation-only.

### CQS002 Query performs I/O { #CQS002 }

Claim
:   design

Detection
:   Query-named function reaching an effect boundary

Message
:   `{symbol}` reads like a query but reaches `{effects}`, making ordinary-looking observation perform external work.

### CQS003 Mutation disguised as calculation { #CQS003 }

Claim
:   risk

Detection
:   Pure-sounding name writing to caller-owned objects

Message
:   `{symbol}` sounds like a calculation but mutates caller-owned `{target}`.

### CQS004 Caller object mutation { #CQS004 }

Claim
:   risk

Detection
:   Mutates a parameter the caller owns

Message
:   `{symbol}` mutates caller-owned `{parameter}`. Should the mutation be visible from the signature?

### CQS005 Destructive mutation hidden from caller { #CQS005 }

Claim
:   risk

Detection
:   own + (nam or shp)

Message
:   `normalize()` deletes and rewrites entries in its input mapping. Should a caller be able to see that from the name?

### CQS006 Persistence hidden in helper { #CQS006 }

Claim
:   risk

Detection
:   A generic helper name reaches a database write or commit boundary.

Message
:   Helper `{helper}` performs `{persistence_effect}`. Should the name communicate durable mutation?

### CQS007 Helper name hides external effects { #CQS007 }

Claim
:   design

Detection
:   A generic or pure-looking helper reaches network, filesystem, database, notification, or subprocess effects.

Message
:   Helper `{helper}` performs `{effects}`. Should a caller be able to infer that from the name?
