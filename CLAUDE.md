# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

`humansays` is a zero-dependency linter that parses Python with the stdlib `ast` and scores how
hard the code is to read and maintain. See `README.md` for the CLI surface, exit codes, and
configuration keys; none of that is repeated here.

## Commands

Use the project scripts rather than invoking `ruff`, `ty`, or `pytest` directly.

| Command | What it does |
| --- | --- |
| `make format` | `scripts/format.sh`. The only script that writes to the repo. |
| `make lint` | `scripts/lint.sh`, read-only, nine checks. |
| `make test` | `scripts/test.sh all`: `compileall`, then the full suite with coverage. |
| `make ci` | Default goal. Lint, docs build, tests, `uv lock --check`, `uv build`. |

Run `make format` before `make lint` instead of hand-fixing lint findings.

One check at a time:
`bash scripts/lint.sh <format|markdown|ruff|typecheck|shell|security|deps|imports|deadcode>`

One scope at a time: `bash scripts/test.sh <unit|integration|tooling>`

### Running a single test

```bash
uv run python -m pytest tests/unit/test_x.py::test_y --no-cov
```

`--no-cov` is not optional. Pytest config lives in `.pytest.toml`, not `pyproject.toml`, and
its `addopts` always turn on `--cov`, while `.coveragerc.ini` sets `fail_under = 85`. Without
the flag a single passing test still exits 1 on `Required test coverage of 85.0% not reached`.
`scripts/test.sh` passes it to the scoped subcommands for the same reason.

`pytest-randomly` reorders tests every run. To pin the order, add `--randomly-seed=last` to
reuse the previous run's seed, or `--randomly-dont-reorganize`. Do not reach for
`-p no:randomly`: `required_plugins` in `.pytest.toml` lists `pytest-randomly`, so disabling it
aborts collection with `Missing required plugins`.

The `unit`, `integration`, and `tooling` markers are applied by directory in
`tests/conftest.py`. Do not decorate tests by hand. `tests/golden/` is marked `integration`.

## Architecture

```
cli.main -> config.loading -> application.collect_files -> analysis.extract
  -> facts -> rules.evaluation -> findings -> scoring -> reporting.render
```

The layer order is a machine-checked contract in `.importlinter.ini`, enforced by
`bash scripts/lint.sh imports`. Two constraints follow from it:

- **`ast` and `tokenize` may only be imported inside `humansays.analysis`.** That package is
  the normalization boundary. Everything downstream reads frozen `facts` dataclasses and never
  sees an AST node. Enforced by the `ast-confined-to-analysis` contract and by
  `tests/integration/test_analysis_confinement.py`.
- **`analysis` and `rules` must not import each other.** They are siblings written with `|` in
  the layers contract so the ban runs both directions. They meet only at `humansays.facts`.
  The same test file also asserts that `facts` and `rules` never branch on `sys.version_info`.

## Adding a rule

Five places, and a half-finished rule is easy to produce:

1. Adapter function in `src/humansays/rules/<group>/adapters.py`. Groups are `contract`,
   `encap`, `err`, `idiom`, `kiss`, `smell`, `solid`, `yagni`.
2. Metadata entry in that group's `rules.toml`. Rule metadata ships as package data and is
   loaded lazily through `importlib.resources` in `rules/loading.py`. Never hardcode it in
   Python.
3. A `SignalName` member in `src/humansays/enums.py`.
4. An import and a tuple entry in `src/humansays/rules/registry.py`, in the tuple matching the
   rule's scope (`MODULE_ADAPTERS`, `FUNCTION_ADAPTERS`, `METHOD_ADAPTERS`,
   `CLASS_HEAD_ADAPTERS`, `CLASS_TAIL_ADAPTERS`, `MODULE_TAIL_ADAPTERS`). Registration is a
   literal tuple rather than decorator discovery, which keeps evaluation order diffable. Keep
   it that way.
5. A page under `docs/site/rules/` and its `nav:` entry.

`Severity` has exactly two members, `WARNING` and `ADVISORY`. It is a separate axis from
`Disposition` (`ON`, `HINT`, `EVIDENCE`, `OFF`), which decides whether a finding is scored and
whether it is shown.

## Conventions

- Imports inside `src/humansays` are absolute: `from humansays.config import ...`, never
  `from .config import ...`. `ban-relative-imports = "all"` in `.ruff.toml` is the enforcer
  (TID252), and `make format` rewrites offenders in place.
- `dependencies = []` in `pyproject.toml` stays empty. Runtime code is stdlib only, and
  `deptry` in `make lint` fails on an undeclared import.
- Ruff formats with single quotes at line length 90.

## Documentation

- `mkdocs.yml` is at `docs/`, not the repo root. Every build needs `-f docs/mkdocs.yml`; a bare
  `mkdocs build` cannot find a config.
- Pages live in `docs/site/`. The build writes to the repo-root `site/`, which is gitignored.
- The build runs `--strict`, so a page without a `nav:` entry fails. Add both in one change.
- `docs/evidence/` sits outside `docs_dir` and is never built.
