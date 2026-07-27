<p align="center">
  <img src="https://raw.githubusercontent.com/rhawk117/humansays/main/docs/site/assets/humansays-mascot.png" width="280" alt="humansays">
</p>

# humansays

[![CI](https://github.com/rhawk117/humansays/actions/workflows/integration.yml/badge.svg)](https://github.com/rhawk117/humansays/actions/workflows/integration.yml)
[![PyPI](https://img.shields.io/pypi/v/humansays.svg)](https://pypi.org/project/humansays/)
[![Python](https://img.shields.io/pypi/pyversions/humansays.svg)](https://pypi.org/project/humansays/)
[![License](https://img.shields.io/pypi/l/humansays.svg)](https://github.com/rhawk117/humansays/blob/main/LICENSE)

A python linter which evaluates how difficult AI generated code is to read, understand, test, maintain, and safely modify. It gives coding agents actionable and easy to reason about feedback on design problems that traditional linters, type checkers, and tests cannot detect.

Full documentation: <https://rhawk117.github.io/humansays/>

`humansays` parses Python with the standard-library AST and points reviewers toward code that deserves a second look. It reports structural signals such as long parameter lists, deep nesting, mutable module state, lazy imports, oversized functions and classes, and methods that use neither `self` nor the class.

It does not claim that a finding is a bug. Each finding is a review lead: a location, a score, and a question worth asking before the code reaches production.

> [!WARNING]
> Rule identifiers are unstable until `0.1.0`. The current `HS###` identifiers may be renamed before then, so do not pin automation to them yet.
>
> The current prerelease is [`v0.1.0a1`](https://github.com/rhawk117/humansays/releases/tag/v0.1.0a1). GitHub does not show it as the repository's latest release because it is marked as a prerelease.

## Why this exists

Linters are good at detecting known mistakes. Type checkers are good at proving whether values satisfy declared interfaces. Neither is responsible for asking whether a function has accumulated too many jobs, whether a class is carrying unrelated state, or whether generated code is technically valid but unpleasant to maintain.

That is the gap `humansays` targets.

It gives a human reviewer, or a tool acting on behalf of one, a smaller set of places to inspect. The output is intentionally framed as questions rather than verdicts because syntax alone cannot prove intent.

## Install

`humansays` requires Python 3.11 or newer.

```bash
pip install humansays
```

There are no runtime dependencies and no extras. Text output is written with
plain ANSI escapes, which `NO_COLOR`, `FORCE_COLOR`, and `TERM=dumb` control.

## Quick start

Scan a directory:

```bash
humansays src/
```

Scan specific files:

```bash
humansays app.py tests/test_app.py
```

Read tracked Python paths from standard input:

```bash
git ls-files "*.py" | humansays
```

Produce machine-readable output:

```bash
humansays --format json src/
```

Fail CI when warnings are present:

```bash
humansays --fail-on warning src/
```

Fail CI when the project score drops below a threshold:

```bash
humansays --min-score 70 src/
```

Inspect one symbol:

```bash
humansays --symbol build_report src/
```

## What it reviews

`humansays` looks for structural signals that often justify manual review, including:

- functions with many arguments, branches, nested blocks, or source lines
- classes with many attributes or base classes
- modules that have grown beyond a configured size
- mutable state defined at module scope
- imports performed inside functions or methods
- methods that do not use `self` or the class

A finding means "inspect this," not "rewrite this." Large functions and mutable state can be reasonable. The tool is useful because those choices should usually be deliberate.

## Command-line options

| Option | Default | Effect |
| --- | ---: | --- |
| `--format text\|json` | `text` | Select the report format |
| `--limit N` | `200` | Show at most `N` targets; `0` shows all |
| `--symbol NAME` | none | Restrict output to one symbol |
| `--exclude PATTERN` | none | Skip matching paths; repeatable |
| `--fail-on never\|warning\|any` | `never` | Exit nonzero when findings reach the selected level |
| `--min-score N` | none | Exit nonzero when the score is below `N` |
| `--config PATH` | auto | Load an explicit configuration file |

## Configuration

`humansays` reads configuration from either:

1. `humansays.toml`
2. `[tool.humansays]` in `pyproject.toml`

The first discovered configuration source is used. Command-line arguments override file settings.

The block below is an example of **loosened** thresholds, not the defaults. Every key and its real default is documented at [Configuration](https://rhawk117.github.io/humansays/configuration/).

```toml
[tool.humansays.report]
format = "text"
limit = 50
fail_on = "warning"
min_score = 70.0

[tool.humansays.selection]
exclude = ["migrations", "generated"]

[tool.humansays.thresholds.functions]
max_arguments = 5
max_nesting = 4
max_branches = 12
max_lines = 60

[tool.humansays.thresholds.classes]
max_attributes = 10
max_base_classes = 2

[tool.humansays.thresholds.modules]
max_lines = 500
```

The same settings can live in a standalone `humansays.toml` file without the `tool.humansays` prefix:

```toml
[report]
format = "text"
limit = 50
fail_on = "warning"
min_score = 70.0

[selection]
exclude = ["migrations", "generated"]

[thresholds.functions]
max_arguments = 5
max_nesting = 4
max_branches = 12
max_lines = 60

[thresholds.classes]
max_attributes = 10
max_base_classes = 2

[thresholds.modules]
max_lines = 500
```

## CI usage

`humansays` does not fail a command merely because it found something. The default `--fail-on never` keeps the report advisory.

Use `--fail-on` or `--min-score` when you want enforcement:

```bash
humansays   --format text   --fail-on warning   --min-score 70   src/
```

For tools that consume structured results:

```bash
humansays --format json src/ > humansays-report.json
```

Rule identifiers may change before `0.1.0`, so prerelease integrations should consume the report as a whole rather than treating the current identifiers as a stable API.

## Exit codes

| Code | Meaning |
| ---: | --- |
| `0` | The command completed without crossing a configured failure threshold |
| `1` | Findings crossed `--fail-on`, or the score fell below `--min-score` |
| `2` | The requested `--symbol` was not found |
| `3` | No Python files were found |
| `4` | The requested configuration file was missing |

## Scope and limitations

`humansays` is not a replacement for Ruff, Pylint, a type checker, tests, or a security scanner.

It does not:

- prove runtime behavior from syntax
- determine whether code was written by a person or a model
- decide that every reported structure is incorrect
- compete with general-purpose linters on speed or rule coverage

It reports syntax-level patterns that commonly benefit from a second reader. The reviewer still decides whether the code is clear, justified, and worth changing.

## Development status

`humansays` is currently alpha software. Configuration, output details, scoring behavior, and rule identifiers may change before the first stable release.

Bug reports and focused examples are useful, especially cases where a finding is consistently noisy or where an obvious structural problem is missed.

## License

MIT
