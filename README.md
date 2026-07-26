# humansays

[![CI](https://github.com/rhawk117/humansays/actions/workflows/integration.yml/badge.svg)](https://github.com/rhawk117/humansays/actions/workflows/integration.yml)
[![PyPI](https://img.shields.io/pypi/v/humansays.svg)](https://pypi.org/project/humansays/)
[![Python](https://img.shields.io/pypi/pyversions/humansays.svg)](https://pypi.org/project/humansays/)

A linting guardrail for LLM-generated Python code which raises structural doubts
and a per-finding score before the code reaches a reviewer.

`humansays` reads the standard-library AST and reports structural review leads —
long parameter lists, deep nesting, mutable module state, lazy imports, methods
that touch neither `self` nor the class. It does not tell you the code is wrong.
It tells you where a reviewer should look, and asks a question about each site.

> **Rule identifiers are unstable until `0.1.0`.** The current `HS###` ids may be
> renamed before then. Do not pin against them.

## Install

```bash
pip install humansays

# with rich terminal output
pip install 'humansays[terminal]'
```

`humansays` has no runtime dependencies. `rich` is an optional extra; without it
the terminal output falls back to plain ANSI.

Requires Python 3.11 or newer.

## Usage

```bash
humansays src/                     # scan a directory
humansays a.py b.py                # scan specific files
humansays --format json src/       # machine-readable output
git ls-files '*.py' | humansays    # read a path list from stdin
```

Useful flags:

| Flag | Effect |
| --- | --- |
| `--format text\|json` | Output format. Default `text` |
| `--limit N` | Show at most N targets. `0` shows all. Default `200` |
| `--symbol NAME` | Restrict output to one symbol |
| `--exclude PATTERN` | Skip matching paths. Repeatable |
| `--fail-on never\|warning\|any` | Exit non-zero on findings. Default `never` |
| `--min-score N` | Exit non-zero below this score |
| `--config PATH` | Explicit configuration file |

Exit codes: `0` clean, `1` findings exceeded the configured threshold, `2`
`--symbol` not found, `3` no Python files found, `4` configuration file missing.

## Configuration

Settings are read from `humansays.toml`, or from a `[tool.humansays]` table in
`pyproject.toml`, whichever is found first. Command line flags override the file.

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

## What it does not claim

It is not faster than Ruff, not more comprehensive than Pylint, and not a
replacement for a type checker. It cannot prove runtime behavior from syntax,
and it does not detect whether a model wrote your code — only whether the code
carries the structure that usually needs a second reader.

## License

MIT
