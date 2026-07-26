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

Each phase directory contains `allowed-paths.txt` — one glob per line, `#` for
comments.

```bash
scripts/check-scope.sh 01-migration
```

Run it as a pre-commit hook and in CI.

## Script

`scripts/check_scope.py`. Python, not bash — bash `[[ ]]` lets `*` cross `/`, so
`src/humansays/**` matched at any depth.

## Pattern file format

```
# comment
src/humansays/**                      allow
!src/humansays/analysis/signature*    deny, overrides any allow
```

Glob semantics are POSIX-like: `*` stays within a path segment, `**` crosses
segments, `?` matches one character within a segment.

## The seven-case test

The previous bash implementation returned `scope ok` for the first three of
these. Any replacement must block the first six and pass the seventh.

| # | Case | Expected |
|---|---|---|
| 1 | Committed change to a denied path | blocked |
| 2 | Staged file outside the allowlist | blocked |
| 3 | Untracked file outside the allowlist | blocked |
| 4 | Unstaged edit outside the allowlist | blocked |
| 5 | Allowlist widened in a commit containing other changes | blocked |
| 6 | Edit to the guard script itself | blocked |
| 7 | Legitimate in-scope change | passes |

`tests/tooling/test_scope_guard.py` implements these against a temporary git
repository. **This is the test named by the enforcement claim in
`agent-protocol.md` §4a.** If it does not exist, the claim that scope is
enforced is unsupported.

## Why four change sources

`git diff BASE...HEAD` sees only committed changes. A guard reading it alone is
bypassed by anything staged, unstaged, or untracked. The guard checks all four
and reports which source flagged each violation.

## Widening the allowlist

Allowed, in a commit containing **only** the allowlist change, with a reason. The
guard enforces the isolation; without it, an agent adds the forbidden file and
the permission in one commit.
