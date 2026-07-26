# Phase 1 — Sections C and D closeout evidence

## Scope and method

This file records **verified state** for Phase 1 Sections C (tooling repair)
and D (prerelease and name reservation) only — not Section B. Every claim
below cites the command that produced it, measured on `docs/phase-1-cd-closeout`
(branched off `develop`). Sections C and D were implemented and merged in an
earlier session (PRs #4, #5, #6, #7, #8); this file is the paper trail for
that work, written after re-verifying nothing regressed.

## Section C acceptance

| Item | Command | Result |
|---|---|---|
| `scripts/check_scope.py` present | `git log --oneline -1 -- scripts/check_scope.py` | `9622059 feat(poc): Initial proof of concept and code analysis [merges #4]` |
| `tests/tooling/test_scope_guard.py` present and passing | `uv run pytest tests/tooling/ -q` | `17 passed` (coverage failure/warnings in the same run are an artifact of running a subset that never imports `humansays`, not a real failure) |
| `scripts/check-scope.sh` absent | `git log --all --oneline -- scripts/check-scope.sh` | no output — never existed in this repository's history |
| `!`-deny lines present in every `allowed-paths.txt` | `grep -c '^!' docs/phases/*/allowed-paths.txt` | 01-review 5, 02-fact-model 2, 03-measurement-harness 1, 04-pilot-rules 2, 05-measurement-study 1, 06-catalog-expansion 2, 07-effects 1, 08-dynamic 1, 09-performance 1 |
| Eight-case test, mapped to test functions | `grep -n "^def test" tests/tooling/test_scope_guard.py` | case 1 `test_committed_change_to_denied_path_is_blocked:97`, case 2 `test_staged_file_outside_allowlist_is_blocked:109`, case 3 `test_untracked_file_outside_allowlist_is_blocked:121`, case 4 `test_unstaged_edit_outside_allowlist_is_blocked:131`, case 5 `test_allowlist_widened_alongside_other_changes_is_blocked:141`, case 6 `test_edit_to_the_guard_itself_is_blocked:152`, case 7 `test_legitimate_in_scope_change_passes:166`, case 8 `test_isolated_allowlist_widening_is_permitted:176` |
| Ninth test, `glob_to_regex` unit-level | `grep -n "^def test" tests/tooling/test_scope_guard.py` | `test_star_stays_within_a_segment_and_doublestar_crosses:209` — parametrized, not an end-to-end case |

## Section D acceptance

| Item | Command | Result |
|---|---|---|
| PyPI project live | `curl -s -o /dev/null -w "%{http_code}" https://pypi.org/project/humansays/0.1.0a1/` | `200` |
| Release recorded on PyPI | `curl -s https://pypi.org/pypi/humansays/json` | `releases` key contains exactly `['0.1.0a1']` |
| `release.yml` permission scopes separated | `grep -n "id-token\|contents:" .github/workflows/release.yml` | top-level `:20` `contents: read`; `publish` job `:95-96` `contents: read` / `id-token: write`; `github-release` job `:129` `contents: write` |
| Version-metadata test present and passing | `grep -n "^def test" tests/tooling/test_version_metadata.py` | `test_installed_metadata_matches_pyproject:25`, `test_cli_version_flag_matches_installed_metadata:29` — both included in the `17 passed` run above |
| README rule-ID instability line | `grep -n "unstable" README.md` | `README.md:15` — `**Rule identifiers are unstable until 0.1.0.**` |
| mkdocs job disabled, not deleted | `ls .github/workflows/ \| grep mkdocs` | `upload-mkdocs.yml` present, triggered only via `workflow_call` — not on push/PR |

## Stated exception 1 — the guard was not run against this PR's diff

Per §C "The guard does not apply retroactively": `01-review/allowed-paths.txt`
is review-shaped and postdates the migration commits it would otherwise be run
against. `scripts/check_scope.py` was **not** invoked against this branch's
diff, and no `allowed-paths.txt` was widened to accommodate it. Scope
enforcement applies from the review commits forward.

## Stated exception 2 — the guard is not invoked by CI or pre-commit

```
$ grep -rn "check_scope" .github/workflows/ .pre-commit-config.yaml
(no output)
```

Only the guard's *test* runs, via `testpaths = ["tests"]` in `.pytest.toml`.
`docs/process/scope-guard.md:25` states "Run it as a pre-commit hook and in
CI," which is therefore not true today.

**Operator disposition:** the guard is a reviewer's tool for grading agent
work, not a CI gate. Wiring it into CI or pre-commit was considered and
declined. The line in `scope-guard.md` is aspirational and is carried
deliberately as a known documentation divergence, not an oversight — tracked
for a follow-up issue rather than fixed in this branch.

## Release visibility finding

```
$ gh api repos/rhawk117/humansays/releases/latest
{"message":"Not Found","documentation_url":"...","status":"404"}
```

GitHub excludes prereleases from the "latest release" concept, so
`/releases/latest` 404s and the repository homepage's Releases sidebar widget
renders nothing. The release itself is correct and renders on the releases
list and its own tag page:

```
$ curl -sL https://github.com/rhawk117/humansays/releases | grep -c v0.1.0a1
13
```

**Disposition:** `prerelease: true` is correct for an alpha and stays.
Discoverability from the repository homepage is addressed by the README link
added in the following commit on this branch.

## Branch state

```
$ git diff origin/develop origin/main --stat
(no output)
$ git log origin/develop..origin/main --oneline
2288b61 fix(release): repair the github-release job [merges #8]
```

Trees are identical; `main` is one merge commit ahead of `develop`. Recorded
as accepted, not reconciled — per operator decision this branch leaves the
divergence as-is.
