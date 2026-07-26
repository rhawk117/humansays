# Identity and selection

## Rule IDs

```
HS-<FAMILY>-<NN>          signals
HS-FIND-<NN>              correlated findings
```

Twelve signal families.

| Family | Covers | Criteria § |
|---|---|---|
| `HS-PURPOSE` | Role classification and contract | §1, §2 |
| `HS-INPUT` | Explicit and hidden dependencies | §3 |
| `HS-STATE` | State ownership and lifetime | §4 |
| `HS-EFFECT` | Side effects and boundaries | §5 |
| `HS-INIT` | Invariants and construction | §6 |
| `HS-SHAPE` | Cohesion, extraction, control flow | §7, §8, §10, §14 |
| `HS-ARGS` | Function arguments | §9 |
| `HS-CLASS` | Class cohesion | §11 |
| `HS-FAIL` | Failure semantics | §12 |
| `HS-TEST` | Testability | §13 |
| `HS-NARRATION` | Compensating commentary and boilerplate | §7, §8 applied |
| `HS-LEAK` | Retention and lifetime, observed only | §4 applied |

## Findings are not promoted signals

**Revision note.** An earlier draft said number ranges distinguished signals from
findings *and* that a promoted signal keeps its ID. Those cannot both hold.

The resolution matches the architecture: a finding *correlates* signals, so it
was never one signal. Findings are distinct rules from inception, in their own
`HS-FIND` namespace. Promotion is not an operation that exists.

Number ranges carry **no semantic meaning**. `HS-STATE-07` is the seventh state
rule and nothing more.

## Why self-describing IDs

The primary consumer is a language model working in a bounded context window.
`HS-STATE-03` conveys its category without a catalog lookup; `HS303` does not.
The extra characters buy back more context than they cost.

Family is the only attribute encoded in the ID because it is the only one that
never changes. Claim type, evidence strength and evidence source all live in the
catalog as metadata and may be revised without an ID change.

## Selection

See [`02-evaluation-model.md`](02-evaluation-model.md) §6 for the four
orthogonal flags and the profile expansions. In brief:

```
--claim            bug,risk,design
--min-evidence     strong | moderate | weak
--include-family   HS-STATE,HS-EFFECT
--exclude-family   HS-NARRATION
--evidence-source  static,calibrated,observed
```

No flag does two jobs. `--claim` is a set, not a ceiling. `--evidence-source` is
additive, never replacing.
