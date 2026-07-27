# CQS rules

These rules flag violations of command-query separation, where operations that
sound like observation also perform mutation or external effects.

None of the rules below are implemented yet. They are planned.

Background reading: Bertrand Meyer's rule as described by
[Martin Fowler](https://martinfowler.com/bliki/CommandQuerySeparation.html),
and the
[command-query separation](https://en.wikipedia.org/wiki/Command%E2%80%93query_separation)
overview.

| ID     | Rule                              | Default | Concern |
| ------ | --------------------------------- | ------- | ------- |
| CQS001 | Query mutates owned state         | on      | hazard  |
| CQS002 | Query performs I/O                | on      | review  |
| CQS003 | Mutation disguised as calculation | on      | hazard  |

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
