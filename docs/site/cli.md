# CLI reference

`humansays` finds structural Python review leads using the standard-library
AST. This page documents every flag as read from
`src/humansays/config/loading.py:111-141`. Version `0.1.0a1` (alpha).

## Precedence

Settings come from three places, later ones winning: dataclass defaults, a
discovered TOML config file, then explicit command-line flags. CLI flags
default to `argparse.SUPPRESS`, so an unset flag is absent from the parsed
namespace and never overrides the config file or the built-in default.

## Positional argument

### `paths`

Zero or more files or directories to scan (`nargs='*'`).

- A directory is scanned recursively for `*.py` files, skipping hidden
    directories and anything matching an exclude pattern.
- A single `-`, or no paths at all, reads a NUL- or newline-separated list of
    paths from standard input. Passing `-` alongside other paths reads stdin
    for that one entry and still scans the rest as given.

```shell
humansays src/ tests/
git ls-files -z '*.py' | humansays -
```

## Flags

### `--version`

Prints `humansays <installed-version>` and exits.

### `--config PATH`

Use this TOML file instead of auto-discovery. If the path does not exist,
humansays exits with an error (exit code 4). Without `--config`, humansays
looks for `humansays.toml` then `pyproject.toml` in the current directory and
uses the first one found. See `configuration.md` for the file format.

### `--format {text,json}`

Destination field: `output_format`. Selects the output format. Default (from
`Report.format`): `text`.

### `--symbol NAME`

Restrict results to findings whose symbol matches `NAME`, either exactly, as
a dotted suffix (`NAME` matches `Class.NAME`), or as a dotted prefix (`NAME`
matches `NAME.method`). If no symbol in the scan matches, humansays exits
with an error (exit code 2). Default: no restriction (`None`).

### `--limit N`

Maximum number of review targets to print. `--limit 0` prints all of them.
Type: int. Default (from `Report.limit`): `200`.

### `--exclude PATTERN`

Adds a directory name to skip during directory traversal. Repeatable
(`action='append'`). This extends, rather than replaces, the built-in
default excludes: `.git`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`,
`.tox`, `.venv`, `__pycache__`, `build`, `dist`, `node_modules`,
`site-packages`, `venv`. Default: no additional excludes.

### `--fail-on {never,warning,any}`

Controls whether findings cause a nonzero exit code (exit code 1):
`never` never fails on findings, `warning` fails if any warning-severity
finding is present, `any` fails if any finding at all is present. Default
(from `Report.fail_on`): `never`.

### `--min-score SCORE`

If the scan's overall score is below `SCORE`, humansays exits with code 1
regardless of `--fail-on`. Type: float, range 0.0-100.0. Default (from
`Report.min_score`): `0.0`.

### Threshold flags

Each of these overrides one field of `[tool.humansays.thresholds]` (see
`configuration.md` for the full threshold model and defaults):

| Flag                     | Type | Overrides                                  | Default |
| ------------------------ | ---- | ------------------------------------------ | ------- |
| `--max-arguments`        | int  | `thresholds.functions.max_arguments`       | 3       |
| `--max-nesting`          | int  | `thresholds.functions.max_nesting`         | 3       |
| `--class-nesting-bonus`  | int  | `thresholds.functions.class_nesting_bonus` | 1       |
| `--max-branches`         | int  | `thresholds.functions.max_branches`        | 5       |
| `--max-function-lines`   | int  | `thresholds.functions.max_lines`           | 50      |
| `--max-code-lines`       | int  | `thresholds.functions.max_code_lines`      | 65      |
| `--max-class-attributes` | int  | `thresholds.classes.max_attributes`        | 6       |
| `--max-base-classes`     | int  | `thresholds.classes.max_base_classes`      | 1       |
| `--max-file-lines`       | int  | `thresholds.modules.max_lines`             | 500     |

`class_nesting_bonus` is added to `max_nesting` when evaluating nesting depth
inside a method rather than a plain function.

## Exit codes

Read from `src/humansays/const.py` and `src/humansays/cli.py`. Enforced by
`tests/integration/test_exit_contract.py`.

| Code | Meaning                                                               |
| ---- | --------------------------------------------------------------------- |
| `0`  | The command completed without crossing a configured failure threshold |
| `1`  | Findings crossed `--fail-on`, or the score fell below `--min-score`   |
| `2`  | The requested `--symbol` was not found                                |
| `3`  | No paths were given, or no Python files were found                    |
| `4`  | The configuration could not be loaded                                 |
| `5`  | One or more files could not be analyzed                               |
| `70` | Internal error — this is a humansays bug                              |

A file that cannot be parsed, read, or decoded is reported and makes the run
exit `5`. Findings take precedence: a run with both findings and unanalyzed
files exits `1`. The score and grade cover only the files that were analyzed,
and the text report names the gap.
