# Agent specs

## If you are a coding agent

Read [`process/agent-protocol.md`](process/agent-protocol.md) first. It
describes how work is executed in this repository. Standing constraints live
in `CLAUDE.md` at the repository root and are loaded automatically; they
apply to everything here.

The current rule catalog and design document live on the documentation site,
under Rules → Python. `NEW_RULES.md` at the repository root was the working
draft during the `docs/realign-specs` migration and no longer exists once
that migration lands. Treat the published site as the source of truth.

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

This tree previously organized work into nine sequential phases under
`phases/`. That structure predated the shift to `NEW_RULES.md` as the
project's source of truth and has been retired: see
[`roadmap-retirement.md`](roadmap-retirement.md) for the phase-by-phase
disposition and [`backlog.md`](backlog.md) for the unordered work it left
behind. Only the next piece of work gets planned at a time; do not
reconstruct a phase sequence from the backlog.
