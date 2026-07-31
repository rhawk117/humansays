# Agent specs

## If you are a coding agent

Read [`process/agent-protocol.md`](process/agent-protocol.md) first. It
describes how work is executed in this repository. Plans live in
[`plans/`](plans/) and are reviewed against the protocol's §4 constraint table
before they are executed, not after. There is no backlog: see below. Standing
constraints live in `CLAUDE.md` at the repository root and are loaded automatically; they
apply to everything here.

The documentation site is the source of truth for both rule sets. The 19 rules
that ship in `0.1.0a2` are under Rules, one page per group, each carrying the
severity, confidence, weight and trigger read from
`src/humansays/rules/*/rules.toml`.
The 175-rule planned catalog is under Planned rules and is not implemented.
The criteria the shipped rules encode are under Design philosophy.
`NEW_RULES.md` at the repository root was the working draft during the
`docs/realign-specs` migration and no longer exists.

## Layout

```
.agent-specs/
├── process/              how agents work here; the review checklist
├── design/               reference documents for the evaluation model and architecture
├── plans/                implementation plans, versioned with the code they change
├── CLAUDE.md.template    the root CLAUDE.md's source; edit here, then copy
└── roadmap-retirement.md what the nine-phase roadmap was, and why it stopped
```

## Reading order for a human

`design/00-overview.md` → `design/01-identity-and-selection.md` →
`design/02-evaluation-model.md` → `design/03-effect-architecture.md` →
`design/04-execution-modes.md` → `design/05-rust.md` →
`design/06-cross-language.md` → `design/07-idea-register.md`

## On the retired phase roadmap

This tree previously organized work into nine sequential phase directories,
then into an unordered `backlog.md`. Both are retired. See
[`roadmap-retirement.md`](roadmap-retirement.md) for the phase-by-phase
disposition.

**There is no backlog.** Work that is worth doing is planned and done; work
that is not is not written down. A list of things nobody is doing accrues
claims that stop being true, and this repository has now had that happen twice.
The measurements the backlog held were moved to
`docs/evidence/backlog-measurements.md` before it was deleted.

Only the next piece of work gets planned at a time.
