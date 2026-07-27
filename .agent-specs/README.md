# Agent specs

## If you are a coding agent

Read [`process/agent-protocol.md`](process/agent-protocol.md) first. It
describes how work is executed in this repository. Standing constraints live
in `CLAUDE.md` at the repository root and are loaded automatically; they
apply to everything here.

The documentation site is the source of truth for both rule sets. The 19 rules
that ship in `0.1.0a1` are under Rules, one page per group, each carrying the
severity, confidence, weight and trigger read from `src/humansays/catalog.py`.
The 158-rule planned catalog is under Planned rules and is not implemented.
The criteria the shipped rules encode are under Design philosophy.
`NEW_RULES.md` at the repository root was the working draft during the
`docs/realign-specs` migration and no longer exists.

## Layout

```
.agent-specs/
├── process/     how agents work here; the review checklist
├── design/      reference documents for the evaluation model and architecture
├── backlog.md   unordered future work, deliberately not sequenced into phases
└── superpowers/ working plans; not part of the design record
```

## Reading order for a human

`design/00-overview.md` → `design/01-identity-and-selection.md` →
`design/02-evaluation-model.md` → `design/03-effect-architecture.md` →
`design/04-execution-modes.md` → `design/05-rust.md` →
`design/06-cross-language.md` → `design/07-idea-register.md`

## On the retired phase roadmap

This tree previously organized work into nine sequential phase
directories. That structure predated the shift to `NEW_RULES.md` as the
project's source of truth and has been retired: see
[`roadmap-retirement.md`](roadmap-retirement.md) for the phase-by-phase
disposition and [`backlog.md`](backlog.md) for the unordered work it left
behind. Only the next piece of work gets planned at a time; do not
reconstruct a phase sequence from the backlog.
