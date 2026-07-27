# CQS rules

These rules flag violations of command-query separation, where operations that sound like observation also perform mutation or external effects.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| CQS001 | Query mutates owned state | risk | hazard | on | HS-PURPOSE-02 | `get_*`/`is_*`/`has_*`/`find_*` with non-empty field writes | `{symbol}` reads like a query but writes `{fields}`, so callers cannot treat it as observation-only. |
| CQS002 | Query performs I/O | design | review | on | HS-PURPOSE-03 | Query-named function reaching an effect boundary | `{symbol}` reads like a query but reaches `{effects}`, making ordinary-looking observation perform external work. |
| CQS003 | Mutation disguised as calculation | risk | hazard | on | HS-PURPOSE-09 | Pure-sounding name writing to caller-owned objects | `{symbol}` sounds like a calculation but mutates caller-owned `{target}`. |
