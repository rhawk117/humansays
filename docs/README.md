# humansays documentation

## If you are a coding agent

**Read only the phase file you are executing.** Everything else describes other
phases and will pull you out of scope.

1. Read [`process/agent-protocol.md`](process/agent-protocol.md) — how work is
   done in this repository.
2. Read your phase's `PHASE.md` under [`phases/`](phases/).
3. Read the specific reference documents that file names, and no others.

Standing constraints live in `CLAUDE.md` at the repository root and are loaded
automatically. They apply to every phase.

## Layout

```
docs/
├── process/          how agents work here; scope guard; review checklist
├── phases/           one directory per phase — the execution unit
├── design/           reference. Read only what a phase file names
├── rules/            the rule catalog
├── criteria/         the authored design documents the rules enforce
└── evidence/         measured facts and decision history
```

## Reading order for a human

`design/00-overview.md` → `evidence/poc-baseline.md` →
`design/02-evaluation-model.md` → `rules/python.md` → `phases/`

## Document status

| Path | Status |
|---|---|
| `phases/01-review` | Reconciliation review — the migration is already built |
| `design/02-evaluation-model.md` | Revision 2. Four fields: claim, certainty, impact, report |
| `rules/python.md` | Revision 2. `HS-LLM` renamed `HS-NARRATION`; `impact` empty pending Phase 5 |
| `evidence/critique-log.md` | Two rounds of rejected ideas and why |
| `criteria/` | **Placeholder.** Drop the two authored criteria documents here |

Superseded ideas are recorded rather than deleted. Before proposing a single
severity tier, a computed 0–20 score, a multiplicative confidence formula,
family-based correlation, hand-assigned impact, or a volume-based effect gate,
read `evidence/critique-log.md` — all were tried and rejected with reasons.
