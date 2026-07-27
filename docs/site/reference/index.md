# Reference

humansays is a static analysis tool for Python. It walks the standard-library
AST and reports structural review leads: functions with too many arguments,
classes with low cohesion, deeply nested control flow, shared mutable state,
and similar patterns that are worth a human's attention before the code ships.
Each finding is scored, and the scores roll up into a single 0-100 value per
scan with an A-F grade.

The project describes itself in `pyproject.toml` as "a linting guardrail for
LLM-generated Python code which raises structural doubts and a per-finding
score before the code reaches a reviewer." It does not replace a linter like
Ruff, a type checker, or human review; it produces leads for a reviewer to
follow up on.

This is version `0.1.0a1`, an alpha release. Interfaces, defaults, and the
rule catalog may still change.

## Installation

The package name is `humansays` and it requires Python 3.11 or later. It has
no required runtime dependencies.

```
pip install humansays
```

Text output uses a `rich`-based table renderer if `rich` is installed, and
falls back to plain ANSI otherwise. `rich` ships as the optional `terminal`
extra, not a required dependency:

```
pip install humansays[terminal]
```

Installing either way gives you the `humansays` console command.

## Running it

`humansays` takes files or directories as positional arguments, or reads a
list of paths from standard input:

```
humansays src/
```

```
git ls-files -z '*.py' | humansays -
```

Both accept the paths humansays is meant to scan and print a summary: file
and line counts, a score for the scan, and a list of review targets (a
symbol in a file, with the signals that fired against it). See `cli.md` for
every flag, `configuration.md` for the `[tool.humansays]` TOML surface,
`output.md` for the text and JSON output shapes and the scoring formula, and
`shipped-rules.md` for the full rule catalog.
