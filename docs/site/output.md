# Output

humansays produces two output formats, selected by `--format`/`report.format`:
`text` (default) and `json`. Both are described here as read from
`src/humansays/reporting/render.py`, `src/humansays/reporting/ansi.py`,
and `src/humansays/reporting/grouping.py`. Version `0.1.0a1` (alpha).

## Text output

Text output is written with plain ANSI escapes and prints one line per target.
There are no runtime dependencies and no extras. The whole report is built as
one string and written in a single call, so it never interleaves with anything
else on the stream.

A text run prints, in order:

1. A header line: `Python investigation targets <label>`, where `<label>` is
   the scanned paths joined by `, `, or `<stdin>` if paths came from standard
   input.
2. A summary line: file count, total line count, review target count, and
   parse error count.
3. A score line: the score value, its letter grade, the total penalty, the
   line count it was divided over, and the density per 100 lines.
4. One row per review target (a symbol in a file that accumulated one or
   more findings): its location as `path:start_line-end_line`, the symbol
   name, and the distinct signal indicators that fired against it, most
   severe first.
5. If more targets exist than `--limit` allows, a line reporting how many
   were truncated, with a hint to pass `--limit 0`.
6. One line per file that could not be parsed (`OSError`, `UnicodeError`,
   `SyntaxError`, or `ValueError` while reading or parsing it).
7. `No suspicious structural indicators found.` if there were no targets and
   no parse errors.

Plain ANSI output honors the informal `NO_COLOR` and `FORCE_COLOR`
environment variables and disables color when `TERM=dumb` or output is not a
terminal.

## JSON output

JSON output is a single object printed with `json.dumps(..., indent=2)`:

```json
{
  "schema_version": 1,
  "root": "<label>",
  "score": {
    "lines": 0,
    "penalty": 0.0,
    "density": 0.0,
    "value": 100.0,
    "grade": "A"
  },
  "summary": {
    "files": 0,
    "lines": 0,
    "targets": 0,
    "signals": 0,
    "errors": 0,
    "truncated": 0
  },
  "targets": [
    {
      "path": "src/example.py",
      "symbol": "SomeClass.some_method",
      "line": 10,
      "end_line": 25,
      "signals": [
        {
          "rule_id": "HS001",
          "indicator": "many-arguments",
          "severity": "warning",
          "confidence": 0.8,
          "weight": 3.0,
          "message": "...",
          "evidence": ["..."],
          "review_question": "..."
        }
      ]
    }
  ],
  "errors": ["path: error message"]
}
```

`targets` is truncated to `--limit` entries the same way as text output;
`summary.truncated` reports how many were left out. `errors` lists one
string per file that failed to parse.

## Scoring model

Read from `src/humansays/scoring.py:1-38` and `src/humansays/const.py`.

Each finding contributes a penalty of `weight * confidence`, where `weight`
and `confidence` come from the rule that fired (see `shipped-rules.md`). The
scan's total penalty is the sum of every finding's penalty.

```
density = total_penalty * 100 / max(1, total_lines)
score   = round(100 / (1 + density / 7.5), 1)
```

`total_lines` is the sum of line counts across every scanned file. Dividing
by line count rather than counting findings directly means a large clean
codebase is not punished for its size, and a small file full of findings
cannot hide behind a low absolute count. `7.5` is `SCORE_TOLERANCE`, chosen
so that roughly one warning per 100 lines lands in the mid-seventies. A file
or scan with no weighted findings scores `100.0`.

## Grade bands

Read from `GRADE_BANDS` in `src/humansays/const.py`. A score maps to a grade
by the first band whose floor it meets or exceeds:

| Score | Grade |
|---|---|
| >= 90.0 | A |
| >= 75.0 | B |
| >= 60.0 | C |
| >= 40.0 | D |
| < 40.0 | F |
