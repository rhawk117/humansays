# Changelog

Notable changes to `humansays`. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[PEP 440](https://peps.python.org/pep-0440/).

## Unreleased

### Added

- `--show-evidence` reveals findings from rules whose disposition is
  `evidence`, which are hidden by default.
- Rules carry a `disposition` of `on`, `hint`, `evidence` or `off`. `hint`
  findings are shown but contribute no penalty; `off` rules are not emitted at
  all.
- JSON output carries the rule's disposition.

### Changed

- **Scores move.** HS015, HS016 and HS021 are now `hint`, so they no longer
  contribute penalty. A file whose only findings are those three now scores as
  clean where it previously did not, and the process exit code changes with it.
  Nothing about detection changed; only what is weighed.
- Rule metadata (severity, confidence, weight, message templates) moved from
  Python literals into per-group `rules.toml` files under
  `src/humansays/rules/`. Output is byte-identical across this change.

### Removed

- `src/humansays/catalog.py` and the `signals/` package, replaced by
  `humansays.rules`. No rule was added or removed; all 19 `HS0NN` identifiers
  are unchanged.

## 0.1.0a2

Published to PyPI, tagged 2026-07-27.

## 0.1.0a1

First published alpha. 19 rules. See `docs/evidence/phase-1-cd-closeout.md` for
the release verification record, which covers this publication and the
`release.yml` pipeline both versions ship through.
