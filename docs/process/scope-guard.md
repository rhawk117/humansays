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
uv run python scripts/check_scope.py 01-review --base origin/main
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

## The eight-case test

The previous bash implementation returned `scope ok` for the first three of
these. Any replacement must block the first six, and pass the seventh and
eighth.

| # | Case | Expected |
|---|---|---|
| 1 | Committed change to a denied path | blocked |
| 2 | Staged file outside the allowlist | blocked |
| 3 | Untracked file outside the allowlist | blocked |
| 4 | Unstaged edit outside the allowlist | blocked |
| 5 | Allowlist widened in a commit containing other changes | blocked |
| 6 | Edit to the guard script itself | blocked |
| 7 | Legitimate in-scope change | passes |
| 8 | Allowlist widened in a commit containing nothing else | passes |

Case 8 is the positive companion to case 5 and the documented escape hatch of
[Widening the allowlist](#widening-the-allowlist). Without it the isolation
check is tested only in its rejecting direction, and a guard that blocked every
widening would pass cases 1 through 7.

`tests/tooling/test_scope_guard.py` implements these against a temporary git
repository. **This is the test named by the enforcement claim in
`agent-protocol.md` §4a.** If it does not exist, the claim that scope is
enforced is unsupported.

### A ninth test, at a different level

`test_star_stays_within_a_segment_and_doublestar_crosses` is a parametrized
unit test on `glob_to_regex`, not an end-to-end case. It asserts that `*` stays
within one path segment while `**` crosses segments.

Of the three defects that broke the bash guard — reading only the committed
diff, comments not subtracting from an earlier glob, and `[[ ]]` letting `*`
cross `/` — the first is covered by cases 2 through 4 and the second by the
allow/deny split. The glob defect had no direct regression coverage. It is the
reason `src/humansays/**` matched at any depth.

## Why four change sources

`git diff BASE...HEAD` sees only committed changes. A guard reading it alone is
bypassed by anything staged, unstaged, or untracked. The guard checks all four
and reports which source flagged each violation.

## Widening the allowlist

Allowed, in a commit containing **only** the allowlist change, with a reason. The
guard enforces the isolation; without it, an agent adds the forbidden file and
the permission in one commit.

No `scripts/check-scope.sh` exists in this repository's history
(`git log --all --oneline -- scripts/check-scope.sh` returns nothing). The bash
implementation described above predates this repository; the Phase 1 checklist
item asking for its deletion is satisfied by its absence.
