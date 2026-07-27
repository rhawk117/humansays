# Shipped rules

This table is a direct reconciliation against `src/humansays/catalog.py:18-206`
and `src/humansays/enums.py:35-54` in the current source tree, not a copy of
any earlier notes about the rule set. Version `0.1.0a1` (alpha) ships
**19 rules**, codes `HS001`-`HS009`, `HS012`-`HS019`, `HS021`, and `HS022`.
`HS010`, `HS011`, and `HS020` are gaps in the numbering, not missing rules.

Severity determines the fixed weight: every `warning` rule carries weight
`3.0` and every `advisory` rule carries weight `1.0`
(`WARNING_WEIGHT`/`ADVISORY_WEIGHT` in `catalog.py`). A finding's penalty is
`weight * confidence`; see `output.md` for how penalties turn into a score.
Each rule also carries a `review_question` string, printed alongside a
finding to prompt the human reviewer — not shown in this table but present
in both the text and JSON output (see `output.md`).

| Code | Signal | Severity | Confidence | Weight |
|---|---|---|---|---|
| HS001 | many-arguments | warning | 0.80 | 3.0 |
| HS002 | boolean-modes | advisory | 0.82 | 1.0 |
| HS003 | deep-nesting | warning | 0.76 | 3.0 |
| HS004 | shared-mutable-state | warning | 0.95 | 3.0 |
| HS005 | broad-exception | warning | 0.96 | 3.0 |
| HS006 | multiple-mutation-owners | warning | 0.70 | 3.0 |
| HS007 | mixed-boundaries | warning | 0.65 | 3.0 |
| HS008 | low-class-cohesion | advisory | 0.65 | 1.0 |
| HS009 | long-function | advisory | 0.55 | 1.0 |
| HS012 | many-class-attributes | advisory | 0.72 | 1.0 |
| HS013 | attribute-prefix-cluster | warning | 0.84 | 3.0 |
| HS014 | validated-argument-bundle | warning | 0.88 | 3.0 |
| HS015 | static-method | warning | 0.99 | 3.0 |
| HS016 | lambda-expression | warning | 0.99 | 3.0 |
| HS017 | long-file | warning | 0.60 | 3.0 |
| HS018 | many-base-classes | warning | 0.78 | 3.0 |
| HS019 | many-branches | warning | 0.74 | 3.0 |
| HS021 | lazy-import | advisory | 0.85 | 1.0 |
| HS022 | dense-function | warning | 0.72 | 3.0 |

`rule_id` in output is the `SignalName` member name (e.g. `HS001`); the
`indicator` field printed next to a finding is the member's string value
(e.g. `many-arguments`) shown in this table's Signal column.
