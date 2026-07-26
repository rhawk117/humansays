# Scope guard

## Why

The most likely failure in this project is a model reading a phase document,
noticing a real bug described elsewhere in the docs, and fixing it — thereby
contaminating a behavior-preserving diff so that intentional changes cannot be
distinguished from accidents.

Phase 1 is specifically vulnerable: the argument-kind bug is described in detail,
it is real, it is tempting, and fixing it during migration destroys the parity
oracle.

Prose non-goals do not prevent this reliably. Path allowlists do.

## Mechanism

Each phase directory contains `paths.json` — see "Pattern file format" below.

```bash
uv run python scripts/check_scope.py 01-review --base origin/main
```

## Script

`scripts/check_scope.py`. Python, not bash — bash `[[ ]]` lets `*` cross `/`, so
`src/humansays/**` matched at any depth.

## Pattern file format

```json
{
  "note": "optional, ignored by the parser",
  "allowed": ["src/humansays/**"],
  "deny": ["src/humansays/analysis/signature*"]
}
```

`allowed` and `deny` are required and may be empty. Unknown top-level keys
are a hard error -- a typo'd key that silently parsed as an empty list would
make the guard pass everything.

Glob semantics are POSIX-like: `*` stays within a path segment, `**` crosses
segments, `?` matches one character within a segment.

## What the guard checks

The guard reads four change sources -- committed, staged, unstaged, and
untracked -- because a committed-diff-only check is trivially bypassed. It
reports which source flagged each violation, and it refuses edits to itself
while a phase is running.

## Enforcement status

**The guard is run by no hook and no CI job.** It is a tool an agent runs at
each task boundary, and a scope violation is something the agent reports to
the operator before proceeding rather than works around. There is no test
asserting the guard's own behavior; `tests/tooling/test_scope_guard.py` was
removed when the guard became an agent-facing tool rather than a gate. Treat
the guard's output as advisory evidence, not as proof that scope held.

## Why four change sources

`git diff BASE...HEAD` sees only committed changes. A guard reading it alone is
bypassed by anything staged, unstaged, or untracked. The guard checks all four
and reports which source flagged each violation.

## Widening the allowlist

Allowed, in a commit containing **only** the allowlist change, with a reason. The
guard enforces the isolation; without it, an agent adds the forbidden file and
the permission in one commit.
