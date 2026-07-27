# Getting started

![The humansays mascot](assets/human-says-happy-clipart.png){ align=right width="150" }

!!! warning "Early development"

    This is `0.1.0a1`. The rule identifiers, the configuration schema, and
    the JSON output shape will change before `0.1.0`. Do not pin automation
    to `HS###` codes yet.

## Install

humansays requires Python 3.11 or newer. It has no runtime dependencies and
no extras, so the install is one package.

<!-- termynal -->

```console
$ pip install humansays
---> 100%
Successfully installed humansays-0.1.0a1
$ humansays --version
humansays 0.1.0a1
```

Text output uses plain ANSI escapes. `NO_COLOR` and `TERM=dumb` turn color
off, `FORCE_COLOR` turns it on when the output is not a terminal.

## Your first run

Point it at one file.

<!-- termynal -->

```console
$ humansays docs/examples/smelly.py
Python investigation targets docs/examples/smelly.py
files=1 lines=56 targets=5 errors=0
score 15.6 (F)  penalty 22.67 over 56 lines  density 40.482/100 lines
docs/examples/smelly.py:29-47  Store.dispatch  many-arguments lambda-expression many-branches boolean-modes lazy-import
docs/examples/smelly.py:8-10  <module>  shared-mutable-state lambda-expression
docs/examples/smelly.py:21-56  Store  many-base-classes
docs/examples/smelly.py:25-27  Store.normalize  static-method
docs/examples/smelly.py:49-56  Store.walk  deep-nesting
```

Reading it top to bottom:

The **summary line** counts files scanned, source lines, review targets, and
files that failed to parse. A review target is one symbol that accumulated at
least one signal, not one signal.

The **score line** reports the score, its letter grade, the total penalty, the
line count the penalty was divided over, and the resulting density per 100
lines. Density is what the score is actually computed from, so the same
penalty in a larger file scores better.

Each **target line** is `path:start-end`, then the symbol, then every signal
name that fired against it. `Store.dispatch` above tripped five.

A **truncation line** follows the targets when there are more of them than
`--limit` allows. Five targets is well under the default limit of 200, so the
run above does not print one. Pass `--limit 0` to lift the cap entirely.

## Scanning a package

Give it a directory and it walks the tree.

<!-- termynal -->

```console
$ humansays src/humansays/reporting/
Python investigation targets src/humansays/reporting/
files=5 lines=335 targets=6 errors=0
score 83.6 (B)  penalty 4.92 over 335 lines  density 1.469/100 lines
src/humansays/reporting/ansi.py:29-36  use_color  boolean-modes
src/humansays/reporting/ansi.py:39-44  _style  boolean-modes
src/humansays/reporting/ansi.py:47-59  indicator_text  boolean-modes
src/humansays/reporting/ansi.py:62-73  score_text  boolean-modes
src/humansays/reporting/ansi.py:76-112  report_lines  boolean-modes
src/humansays/reporting/render.py:43-50  report_text  boolean-modes
```

`--exclude` takes a glob and can be repeated. Passing `-` or no path at all
reads a NUL-separated or newline-separated file list from standard input,
which is what makes the pre-commit integration below work.

## Grade bands

| Score        | Grade |
| ------------ | ----- |
| 90 and above | A     |
| 75 to 89     | B     |
| 60 to 74     | C     |
| 40 to 59     | D     |
| below 40     | F     |

A grade is a summary of density, not a pass mark. Nothing in the tool treats
a `B` as acceptable or an `F` as broken. If you want a threshold, set one
yourself with `--min-score`.

## Choosing a failure mode for CI

By default humansays always exits `0`. Findings are reported, not enforced.
Two flags change that.

`--fail-on` takes `never` (the default), `warning`, or `any`. With `warning`
the run exits nonzero if any `WARNING` severity signal fired. With `any` it
exits nonzero if anything fired at all.

`--min-score` takes a number and fails the run if the score falls below it.

<!-- termynal -->

```console
$ humansays --fail-on any src/humansays/reporting/
Python investigation targets src/humansays/reporting/
files=5 lines=335 targets=6 errors=0
score 83.6 (B)  penalty 4.92 over 335 lines  density 1.469/100 lines
src/humansays/reporting/ansi.py:29-36  use_color  boolean-modes
src/humansays/reporting/ansi.py:39-44  _style  boolean-modes
src/humansays/reporting/ansi.py:47-59  indicator_text  boolean-modes
src/humansays/reporting/ansi.py:62-73  score_text  boolean-modes
src/humansays/reporting/ansi.py:76-112  report_lines  boolean-modes
src/humansays/reporting/render.py:43-50  report_text  boolean-modes
$ echo $?
1
```

A failed run writes its **text** report to standard error rather than standard
output, so a pipeline reading stdout gets nothing on failure. JSON output
always goes to standard output, including on failure, so
`humansays --format json | jq` works regardless of the exit code. The exit
codes are `0` clean, `1` findings, `2` symbol not found, `3` no paths given or
no Python files found, `4` configuration could not be loaded, `5` input could
not be analyzed, and `70` internal error. See [CLI reference](cli.md#exit-codes)
for the full table.

Starting with `--fail-on never` on an existing codebase is the honest choice.
Look at what it reports, decide which signals you agree with, tune the
thresholds in [Configuration](configuration.md), and only then turn on
enforcement.

## Pre-commit

```yaml
- repo: local
  hooks:
    - id: humansays
      name: humansays
      entry: humansays
      language: python
      types: [python]
      args: [--fail-on, warning]
```

`types: [python]` makes pre-commit pass the staged Python files as arguments,
so the hook only scans what changed.

## GitHub Actions

```yaml
- name: Structural review
  run: |
    pip install humansays
    humansays --fail-on warning --min-score 70 src/
```

## Next

- [Configuration](configuration.md) for every key, its default, and the TOML
    block that sets it
- [CLI](cli.md) for every flag
- [Output and scoring](output.md) for the JSON shape and how the score is
    computed
