# CLAUDE.md

Project-specific instructions for working in this repo.

## Formatting and linting

Use the project's own scripts instead of invoking `ruff`/`ty`/etc. by hand:

- `scripts/format.sh` (or `make format`) — applies `ruff format` and
  `ruff check --fix --unsafe-fixes` in place. This is the only quality script
  that modifies repository files.
- `scripts/lint.sh` (or `make lint`) — read-only: `ruff format --check`,
  `ruff check --no-fix`, `ty check`, `shellcheck`/`shfmt --diff`, `bandit`,
  `deptry`, `lint-imports --config .importlinter.ini`, `vulture`. Run
  `scripts/lint.sh <name>` for a single check (see the script's `main()` for
  the full list of subcommands).

Run `scripts/format.sh` before `scripts/lint.sh` when iterating locally,
rather than reasoning about individual `ruff`/`ty` invocations.
