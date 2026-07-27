# Planned rule catalog

!!! info "Not implemented"

    This catalog describes 175 rules that are planned, not shipped. Version
    `0.1.0a1` implements [19 rules](../rules/index.md). Nothing on these pages
    runs today. See [Reconciliation](reconciliation.md) for how the shipped
    rules map onto this catalog.

This catalog describes the designed rule set, one page per domain: SOLID, KISS, CQS, POLA, LOD, CONTRACT, ENCAP, LIFE, ERR, CONC, SBD, IDIOM, YAGNI, SMELL, and DRY. This page explains the shared model before you go read any of the domain pages.

Each rule carries an ID, a domain, and a few pieces of metadata that decide whether it fires and whether it counts toward a score.

## Rule model

A rule has independent identity, domain, claim, concern, certainty, emission, and scoring metadata:

- **ID** is a stable domain-prefixed selector such as `ENCAP001`; severity never appears in the ID.
- **Domain** controls shared analysis configuration and its score contribution.
- **Claim** is `defect`, `risk`, or `design` and describes what the rule asserts.
- **Concern** is `hazard`, `review`, or `advisory` and controls reporting/failure policy independently of domain.
- **Default** is `on`, `hint`, `evidence`, `observe`, or `off`.
- **`weight = 0` reports findings but removes their score contribution; it never disables a rule.**

| Default    | Behavior                                                             |         Score |
| ---------- | -------------------------------------------------------------------- | ------------: |
| `on`       | Emitted by the default profile when its concern is reported          |           yes |
| `hint`     | Emitted by the review profile; intentionally unweighted              |            no |
| `evidence` | Hidden unless cited by a finding or requested with `--show-evidence` |            no |
| `observe`  | Requires opt-in runtime observation and never proves absence         | no by default |
| `off`      | Experimental; enabled only by explicit domain/rule selection         |            no |

## Domains and default weights

| Domain     | Purpose                                                                     | Weight | Default selection |
| ---------- | --------------------------------------------------------------------------- | -----: | ----------------- |
| `SOLID`    | Responsibility concentration, extension points, and dependency direction.   |   1.15 | on                |
| `KISS`     | Accidental complexity, control-flow pressure, and unnecessary indirection.  |   1.00 | on                |
| `CQS`      | Separation of observation, mutation, and commands.                          |   1.00 | on                |
| `POLA`     | Behavior that contradicts names, syntax, or ordinary API expectations.      |   1.00 | on                |
| `LOD`      | Reaching past the object you were handed.                                   |   1.00 | on                |
| `CONTRACT` | Explicit input, output, type, and behavioral contracts.                     |   0.90 | on                |
| `ENCAP`    | State ownership, invariants, transitions, and representable state space.    |   1.25 | on                |
| `LIFE`     | Construction, resource ownership, cleanup, and temporal lifecycle.          |   1.15 | on                |
| `ERR`      | Failure boundaries, recovery, retries, rollback, and partial effects.       |   1.25 | on                |
| `CONC`     | Task, thread, process, lock, and concurrent-state ownership.                |   1.25 | on                |
| `SBD`      | Trust boundaries, unbounded resources, and constructs that defeat auditing. |   1.25 | on                |
| `IDIOM`    | Python-specific semantics whose equivalent rules differ by language.        |   0.90 | on                |
| `YAGNI`    | Capability present in the source that nothing in the source uses.           |   0.00 | review only       |
| `SMELL`    | Deliberately opinionated reviewer hints; always unweighted by default.      |   0.00 | review only       |
| `DRY`      | Duplicated knowledge and drift risk; experimental and unweighted.           |   0.00 | off               |

`SOLID` is an ID domain here rather than a principle tag, because its 28 rules share analysis configuration and a single score contribution, which is what a domain is for. The five principles the acronym stands for do not appear as selectors, subgroups, or headings anywhere in the catalog. `CUPID` and `GRASP` remain principle tags, not ID domains.

`YAGNI` works as a static domain because its seven rules observe capability that nothing in the source as written uses — an unread parameter, an unreachable branch, a configuration knob no call site passes. None of them infers future need from a single snapshot, which is the objection that kept the domain out. It ships unweighted while that framing is proven out.

`DRY` stays experimental until it detects duplicated knowledge rather than similar syntax.

## Profiles and selection

```toml
[tool.humansays]
profile = "default"
extend-select = ["SMELL", "IDIOM008"]
ignore = ["SMELL011"]

[tool.humansays.concerns]
report = ["hazard", "review"]
fail-on = ["hazard"]

[tool.humansays.domains.ENCAP]
weight = 1.25
min_boolean_dimensions = 3
min_nullable_dimensions = 3
min_state_product = 8

[tool.humansays.domains.SMELL]
weight = 0.0

[tool.humansays.per-file-ignores]
"tests/**" = ["DRY"]
"migrations/**" = ["SMELL", "DRY"]
```

Selection order is profile → `select` replacement when present → `extend-select` → `ignore` → per-file ignores; ignores always win, and there is no `@` selector syntax.

## Domain thresholds

| Domain     | Default knobs                                                                                                                                                                                                                                      |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SOLID`    | `minimum_lines = 40`, `minimum_independent_dimensions = 3`, `max_public_methods = 10`, `max_mutable_attributes = 8`, `max_operation_dependencies = 5`, `data_clump_size = 3`, `data_clump_occurrences = 2`, `min_detached_method_characters = 240` |
| `KISS`     | `max_function_lines = 60`, `max_nesting = 4`, `max_branches = 12`, `max_loop_statements = 12`, `max_condition_operands = 3`                                                                                                                        |
| `LOD`      | `max_chain_depth = 2`, `allow_chaining = []`                                                                                                                                                                                                       |
| `CONTRACT` | `max_operation_arguments = 5`, `max_positional_record_fields = 2`, `max_dataclass_positional_fields = 3`, `max_generic_parameters = 2`                                                                                                             |
| `ENCAP`    | `min_boolean_dimensions = 3`, `min_nullable_dimensions = 3`, `min_state_product = 8`, `max_sentinels = 3`                                                                                                                                          |
| `ERR`      | `max_exception_handlers = 6`, `require_bounded_retry = true`                                                                                                                                                                                       |
| `SMELL`    | `weight = 0.0`; no rule-specific scoring knobs                                                                                                                                                                                                     |
| `DRY`      | `weight = 0.0`, `minimum_occurrences = 3`; experimental                                                                                                                                                                                            |

`SOLID` carries the dependency-surface knobs because every rule that used them moved into it. `min_detached_method_characters` bounds SOLID028, counting characters that are not comments, docstrings, or whitespace. `max_chain_depth` and `allow_chaining` bound LOD003; the second is a list of dotted names whose fluent interfaces are exempt.

Exact IDs control only selection and suppression; shared knobs live under the domain because per-rule configuration would make the surface impossible to audit.

Every message template is one sentence and must substitute measured values when available; state-product messages must report the actual representable-state count.

## Domains

- [SOLID](solid.md)
- [KISS](kiss.md)
- [CQS](cqs.md)
- [POLA](pola.md)
- [LOD](lod.md)
- [CONTRACT](contract.md)
- [ENCAP](encap.md)
- [LIFE](life.md)
- [ERR](err.md)
- [CONC](conc.md)
- [SBD](sbd.md)
- [IDIOM](idiom.md)
- [YAGNI](yagni.md)
- [SMELL](smell.md)
- [DRY](dry.md)

Rules that changed identifier are listed in [Migration](migration.md), which is
the complete public record of the regroup.
