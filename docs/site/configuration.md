# Configuration file

humansays reads settings from a TOML file, read from
`src/humansays/config/models.py:14-101` and
`src/humansays/config/loading.py:88-108`. Version `0.1.0a1` (alpha).

## Discovery

Without `--config`, humansays looks in the current directory for
`humansays.toml` first, then `pyproject.toml`, and uses whichever it finds
first.

- In `humansays.toml`, settings sit at the top level of the file.
- In `pyproject.toml`, settings sit under `[tool.humansays]`.

Using `[tool.humansays]` inside `humansays.toml` is an error, and humansays
says so and exits `4` rather than failing obscurely.

Any key not recognized by the settings model raises an error at load time
naming the unknown keys, rather than being silently ignored. A malformed or
unreadable config file also exits `4`. See
[Exit codes](cli.md#exit-codes).

## Full default configuration

Written as a `pyproject.toml` fragment; a standalone `humansays.toml` uses
the same keys without the `[tool.humansays.*]` prefix.

```toml
[tool.humansays.thresholds.functions]
max_arguments = 3
max_nesting = 3
class_nesting_bonus = 1
max_branches = 5
max_lines = 50
max_code_lines = 65

[tool.humansays.thresholds.classes]
max_attributes = 6
max_base_classes = 1

[tool.humansays.thresholds.modules]
max_lines = 500

[tool.humansays.selection]
paths = []
exclude = []
symbol = null

[tool.humansays.report]
format = "text"
limit = 200
fail_on = "never"
min_score = 0.0
```

## `thresholds.functions`

| Key | Default | Meaning |
|---|---|---|
| `max_arguments` | `3` | Arguments allowed before a function is flagged. |
| `max_nesting` | `3` | Nesting depth allowed in a plain function. |
| `class_nesting_bonus` | `1` | Added to `max_nesting` for methods, since a method body already carries one implicit level. |
| `max_branches` | `5` | Branches (`if`/`elif`/etc.) allowed before a function is flagged. |
| `max_lines` | `50` | Physical lines allowed in a function body. |
| `max_code_lines` | `65` | Non-blank, non-comment lines allowed in a function body. |

All six values must be non-negative; `max_lines` and `max_code_lines` must be
at least `1`.

## `thresholds.classes`

| Key | Default | Meaning |
|---|---|---|
| `max_attributes` | `6` | Instance attributes allowed on a class before it is flagged. |
| `max_base_classes` | `1` | Base classes allowed before a class is flagged. |

Both values must be non-negative.

## `thresholds.modules`

| Key | Default | Meaning |
|---|---|---|
| `max_lines` | `500` | Lines allowed in a module before it is flagged. |

Must be at least `1`.

## `selection`

| Key | Default | Meaning |
|---|---|---|
| `paths` | `[]` | Files or directories to scan. Normally supplied as CLI positional arguments rather than in the config file. |
| `exclude` | `[]` | Extra directory names to skip, added to the built-in default excludes (`.git`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `.tox`, `.venv`, `__pycache__`, `build`, `dist`, `node_modules`, `site-packages`, `venv`). |
| `symbol` | `null` | Restrict findings to one symbol (see `--symbol` in `cli.md` for the matching rule). |

## `report`

| Key | Default | Meaning |
|---|---|---|
| `format` | `"text"` | `"text"` or `"json"`. |
| `limit` | `200` | Maximum review targets shown; `0` shows all. |
| `fail_on` | `"never"` | `"never"`, `"warning"`, or `"any"`. Controls the nonzero exit code on findings. |
| `min_score` | `0.0` | Minimum acceptable score (`0.0`-`100.0`) before the run exits nonzero. |

Every CLI flag documented in `cli.md` maps onto exactly one of these keys and
overrides it when passed.
