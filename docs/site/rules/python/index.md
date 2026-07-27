# Python rule catalog

This catalog lists every rule humansays can select, one page per domain: SRP, KISS, CQS, POLA, COUP, CONTRACT, STATE, LIFE, FAIL, CONC, IDIOM, NIT, and DRY. Four more pages cover where the rules came from and how they're tracked: the evidence registry, the list of externalized and omitted rules, the crosswalk against the original prototype, and the accounting that ties it all together. This page explains the shared model before you go read any of the domain pages.

Each rule carries an ID, a domain, and a few pieces of metadata that decide whether it fires and whether it counts toward a score.

## Rule model

A rule has independent identity, domain, claim, concern, certainty, emission, and scoring metadata:

- **ID** is a stable domain-prefixed selector such as `STATE001`; severity never appears in the ID.
- **Domain** controls shared analysis configuration and its score contribution.
- **Claim** is `defect`, `risk`, or `design` and describes what the rule asserts.
- **Concern** is `hazard`, `review`, or `advisory` and controls reporting/failure policy independently of domain.
- **Default** is `on`, `hint`, `evidence`, `observe`, or `off`.
- **`weight = 0` reports findings but removes their score contribution; it never disables a rule.**

| Default | Behavior | Score |
|---|---|---:|
| `on` | Emitted by the default profile when its concern is reported | yes |
| `hint` | Emitted by the review profile; intentionally unweighted | no |
| `evidence` | Hidden unless cited by a finding or requested with `--show-evidence` | no |
| `observe` | Requires opt-in runtime observation and never proves absence | no by default |
| `off` | Experimental; enabled only by explicit domain/rule selection | no |

## Domains and default weights

| Domain | Purpose | Weight | Default selection |
|---|---|---:|---|
| `SRP` | Cohesion, responsibility concentration, and reasons to change. | 1.15 | on |
| `KISS` | Accidental complexity, control-flow pressure, and unnecessary indirection. | 1.00 | on |
| `CQS` | Separation of observation, mutation, and commands. | 1.00 | on |
| `POLA` | Behavior that contradicts names, syntax, or ordinary API expectations. | 1.00 | on |
| `COUP` | Dependency visibility, dependency surface, and change coupling. | 1.00 | on |
| `CONTRACT` | Explicit input, output, type, and behavioral contracts. | 0.90 | on |
| `STATE` | State ownership, invariants, transitions, and representable state space. | 1.25 | on |
| `LIFE` | Construction, resource ownership, cleanup, and temporal lifecycle. | 1.15 | on |
| `FAIL` | Failure boundaries, recovery, retries, rollback, and partial effects. | 1.25 | on |
| `CONC` | Task, thread, process, lock, and concurrent-state ownership. | 1.25 | on |
| `IDIOM` | Python-specific semantics whose equivalent rules differ by language. | 0.90 | on |
| `NIT` | Deliberately opinionated reviewer hints; always unweighted by default. | 0.00 | review only |
| `DRY` | Duplicated knowledge and drift risk; experimental and unweighted. | 0.00 | off |

`SOLID`, `CUPID`, `GRASP`, and similar concepts are principle tags or documented selector groups, not ID domains; `YAGNI` is not a static domain because future need cannot be inferred from one source snapshot, and `DRY` stays experimental until it detects duplicated knowledge rather than similar syntax.

## Profiles and selection

```toml
[tool.humansays]
profile = "default"
extend-select = ["NIT", "IDIOM008"]
ignore = ["NIT002"]

[tool.humansays.concerns]
report = ["hazard", "review"]
fail-on = ["hazard"]

[tool.humansays.domains.STATE]
weight = 1.25
min_boolean_dimensions = 3
min_nullable_dimensions = 3
min_state_product = 8

[tool.humansays.domains.NIT]
weight = 0.0

[tool.humansays.per-file-ignores]
"tests/**" = ["DRY"]
"migrations/**" = ["NIT", "DRY"]
```

Selection order is profile → `select` replacement when present → `extend-select` → `ignore` → per-file ignores; ignores always win, and there is no `@` selector syntax.

## Domain thresholds

| Domain | Default knobs |
|---|---|
| `SRP` | `minimum_lines = 40`, `minimum_independent_dimensions = 3`, `max_public_methods = 10`, `max_mutable_attributes = 8` |
| `KISS` | `max_function_lines = 60`, `max_nesting = 4`, `max_branches = 12`, `max_loop_statements = 12`, `max_condition_operands = 3` |
| `COUP` | `max_operation_dependencies = 5`, `data_clump_size = 3`, `data_clump_occurrences = 2` |
| `CONTRACT` | `max_operation_arguments = 5`, `max_positional_record_fields = 2`, `max_dataclass_positional_fields = 3`, `max_generic_parameters = 2` |
| `STATE` | `min_boolean_dimensions = 3`, `min_nullable_dimensions = 3`, `min_state_product = 8`, `max_sentinels = 3` |
| `FAIL` | `max_exception_handlers = 6`, `require_bounded_retry = true` |
| `NIT` | `weight = 0.0`; no rule-specific scoring knobs |
| `DRY` | `weight = 0.0`, `minimum_occurrences = 3`; experimental |

Exact IDs control only selection and suppression; shared knobs live under the domain because per-rule configuration would make the surface impossible to audit.

Every message template is one sentence and must substitute measured values when available; state-product messages must report the actual representable-state count.

## Domains

- [SRP](srp.md)
- [KISS](kiss.md)
- [CQS](cqs.md)
- [POLA](pola.md)
- [COUP](coup.md)
- [CONTRACT](contract.md)
- [STATE](state.md)
- [LIFE](life.md)
- [FAIL](fail.md)
- [CONC](conc.md)
- [IDIOM](idiom.md)
- [NIT](nit.md)
- [DRY](dry.md)

## Provenance

- [Evidence registry](evidence-registry.md)
- [Externalized and omitted](externalized.md)
- [Prototype crosswalk](prototype-crosswalk.md)
- [Accounting](accounting.md)
