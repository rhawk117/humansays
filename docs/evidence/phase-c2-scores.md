# Phase C2 — score movement from the three hint demotions

Measured 2026-07-30 on `chore/rules-relocation`, from `.migration/capture.sh`
captures taken before Task 3 and after Task 5. These are measurements. Re-run
them rather than re-deriving them:

```bash
uv run humansays tests/golden/poc-parity/corpus/django --format json
```

`.migration/` was the capture directory during the phase and is gitignored, so
the command above is the reproduction path that survives it. It reproduces the
"after" row; the "before" row requires checking out `95ec5b6~1` first.

HS015, HS016 and HS021 became `hint`. They are still emitted and still shown;
they no longer contribute penalty. Nothing else changed.

## Scores

| Fixture | Findings | Penalty | Density | Score | Grade |
|---|---|---|---|---|---|
| `poc` before | 0 | 0 | 0.0 | 100.0 | A |
| `poc` after | 0 | 0 | 0.0 | 100.0 | A |
| `django` before | 9 | 12.42 | 1.386 | 84.4 | B |
| `django` after | 9 | 8.6 | 0.96 | 88.7 | B |

The finding list is byte-for-byte the same rule ids in the same order on both
fixtures. Only the score half moved, which is the phase's acceptance condition:
a finding that changed would mean something other than scoring did.

## The arithmetic

Each delta is the summed `weight * confidence` of that fixture's findings whose
rule was demoted, so the change is checkable rather than asserted.

| Fixture | Demoted findings present | Expected delta | Measured delta |
|---|---|---|---|
| `poc` | none | 0 | 0 |
| `django` | HS016 (3.0 x 0.99), HS021 (1.0 x 0.85) | 3.82 | 3.82 |

## What this does not measure

**`poc` is not evidence.** It produces zero findings — 14 files, score 100.0
before and after — so its two rows show a change of nothing from nothing. It is
the prototype's own source, and the prototype's self-findings were all comment
and docstring counting, retired here as HS010 and HS011. Every number above
that means anything comes from `django`: 3 files, 9 findings. Replacing the
corpus is filed in `.agent-specs/backlog.md`.

**HS015 is demoted but unmeasured.** It fires in neither capture corpus and not
in `src/humansays` either, so no row above reflects it. Its demotion is held by
the frozen metadata table in `tests/unit/test_rule_definitions.py` and by the
per-rule fixture tests, and by nothing here.

**The self-scan baseline was checked, not assumed.** `src/humansays` fires only
HS005 and HS002, neither of them demoted, so
`test_self_scan_matches_baseline_exactly` needed no edit.
